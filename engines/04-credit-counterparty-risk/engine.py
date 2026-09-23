from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass(frozen=True)
class Counterparty:
    name: str
    sector: str
    ead: float
    pd: float
    lgd: float
    asset_correlation: float = 0.15

    def validated(self):
        if self.ead < 0 or not 0 <= self.pd <= 1 or not 0 <= self.lgd <= 1 or not 0 <= self.asset_correlation < 1:
            raise ValueError(f"Invalid counterparty parameters for {self.name}")
        return self


@dataclass(frozen=True)
class CreditScenario:
    name: str
    counterparties: tuple[Counterparty, ...]
    reserve: float


@dataclass(frozen=True)
class CreditResult:
    total_losses: np.ndarray
    name_losses: np.ndarray
    defaults: np.ndarray
    names: tuple[str, ...]


PRESETS = {
    "Personal Receivables / Lending": CreditScenario("Personal Receivables / Lending",(
        Counterparty("Private note A","Personal",12000,.05,.65,.10),Counterparty("Private note B","Personal",8000,.08,.70,.10),Counterparty("Rent receivable","Housing",4500,.04,.50,.08),Counterparty("Marketplace balance","Platform",6000,.03,.80,.12)),8000),
    "Solo Professional Invoices": CreditScenario("Solo Professional Invoices",(
        Counterparty("Client A","Services",25000,.03,.70,.12),Counterparty("Client B","Services",18000,.05,.70,.12),Counterparty("Client C","Technology",12000,.04,.65,.15),Counterparty("Client D","Retail",9000,.07,.75,.18),Counterparty("Client E","Other",6000,.06,.70,.10)),20000),
    "Small B2B Receivables": CreditScenario("Small B2B Receivables",(
        Counterparty("Anchor customer","Retail",350000,.025,.55,.18),Counterparty("Customer B","Retail",180000,.04,.60,.18),Counterparty("Customer C","Industrial",150000,.03,.55,.16),Counterparty("Customer D","Technology",120000,.035,.50,.14),Counterparty("Customer E","Services",90000,.05,.65,.15),Counterparty("Customer F","Industrial",80000,.045,.60,.16)),250000),
    "Mid-Market Counterparties": CreditScenario("Mid-Market Counterparties",(
        Counterparty("CP1","Retail",4500000,.02,.50,.20),Counterparty("CP2","Industrial",3800000,.025,.55,.18),Counterparty("CP3","Industrial",3000000,.03,.60,.18),Counterparty("CP4","Energy",2800000,.035,.65,.22),Counterparty("CP5","Technology",2200000,.025,.50,.16),Counterparty("CP6","Retail",1800000,.04,.60,.20),Counterparty("CP7","Services",1500000,.045,.65,.15)),5000000),
    "Enterprise Counterparties": CreditScenario("Enterprise Counterparties",(
        Counterparty("Global CP A","Financial",90000000,.012,.45,.24),Counterparty("Global CP B","Energy",70000000,.018,.60,.22),Counterparty("Global CP C","Industrial",65000000,.02,.55,.20),Counterparty("Global CP D","Technology",55000000,.015,.50,.18),Counterparty("Global CP E","Retail",45000000,.03,.65,.22),Counterparty("Global CP F","Financial",40000000,.017,.45,.24),Counterparty("Global CP G","Industrial",35000000,.025,.60,.20),Counterparty("Global CP H","Services",30000000,.028,.60,.18)),120000000),
}


def analytical_expected_loss(cps, pd_multiplier=1.0, lgd_add=0.0):
    return float(sum(c.ead*min(c.pd*pd_multiplier,1)*min(max(c.lgd+lgd_add,0),1) for c in cps))


def simulate_credit(cps, n_simulations=50000, seed=42, pd_multiplier=1.0, lgd_add=0.0, stochastic_lgd=True):
    cps=[c.validated() for c in cps]; n=len(cps); rng=np.random.default_rng(seed)
    global_factor=rng.standard_normal(n_simulations)
    sectors=sorted(set(c.sector for c in cps)); sector_factors={s:rng.standard_normal(n_simulations) for s in sectors}
    losses=np.zeros((n_simulations,n)); defs=np.zeros((n_simulations,n),dtype=bool)
    for j,c in enumerate(cps):
        rho=c.asset_correlation
        latent=np.sqrt(rho/2)*global_factor + np.sqrt(rho/2)*sector_factors[c.sector] + np.sqrt(1-rho)*rng.standard_normal(n_simulations)
        pd=min(c.pd*pd_multiplier,.999999); default=latent < norm.ppf(pd); defs[:,j]=default
        mean_lgd=min(max(c.lgd+lgd_add,0.001),.999)
        if stochastic_lgd:
            concentration=25.0; a=mean_lgd*concentration; b=(1-mean_lgd)*concentration
            lgd=rng.beta(a,b,n_simulations)
        else:
            lgd=np.full(n_simulations,mean_lgd)
        losses[:,j]=default*c.ead*lgd
    return CreditResult(losses.sum(axis=1),losses,defs,tuple(c.name for c in cps))


def summarize(result:CreditResult,cps,reserve:float):
    v95=float(np.quantile(result.total_losses,.95)); v99=float(np.quantile(result.total_losses,.99))
    return {"analytical_el":analytical_expected_loss(cps),"simulated_el":float(result.total_losses.mean()),"unexpected_loss":float(result.total_losses.std(ddof=1)),
            "var_95":v95,"var_99":v99,"es_95":float(result.total_losses[result.total_losses>=v95].mean()),"reserve_breach_probability":float((result.total_losses>reserve).mean())}


def contributions(result:CreditResult,cps,confidence=.95):
    el=result.name_losses.mean(axis=0); threshold=np.quantile(result.total_losses,confidence); tail=result.name_losses[result.total_losses>=threshold].mean(axis=0)
    return pd.DataFrame({"counterparty":result.names,"ead":[c.ead for c in cps],"expected_loss":el,"el_contribution":el/el.sum() if el.sum() else 0,"tail_loss":tail,"tail_contribution":tail/tail.sum() if tail.sum() else 0}).sort_values('tail_contribution',ascending=False)


def concentration_metrics(cps):
    ead=np.array([c.ead for c in cps]); shares=ead/ead.sum(); return {"total_ead":float(ead.sum()),"largest_exposure_share":float(shares.max()),"ead_hhi":float((shares**2).sum()),"effective_counterparties":float(1/(shares**2).sum())}


def stress_grid(cps,reserve,n=20000,seed=42):
    rows=[]
    for pdm,lgda,label in [(1,0,'Base'),(1.5,.05,'Moderate'),(2,.10,'Severe'),(3,.15,'Extreme')]:
        r=simulate_credit(cps,n,seed,pdm,lgda); m=summarize(r,cps,reserve); rows.append({"scenario":label,"pd_multiplier":pdm,"lgd_add_pp":100*lgda,**m})
    return pd.DataFrame(rows)
