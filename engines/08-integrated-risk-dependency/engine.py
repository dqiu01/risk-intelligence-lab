from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.stats import norm, lognorm, gamma


@dataclass(frozen=True)
class RiskNode:
    name: str
    category: str
    mean_loss: float
    coefficient_of_variation: float
    distribution: str = "lognormal"
    common_factor_loading: float = 0.4

    def validated(self):
        if self.mean_loss < 0 or self.coefficient_of_variation < 0 or not 0 <= self.common_factor_loading < 1:
            raise ValueError(f"Invalid risk node {self.name}")
        if self.distribution not in {"lognormal","gamma"}:
            raise ValueError("distribution must be lognormal or gamma")
        return self


@dataclass(frozen=True)
class IntegratedScenario:
    name: str
    risks: tuple[RiskNode,...]
    reserve: float


@dataclass(frozen=True)
class IntegratedResult:
    total_losses: np.ndarray
    component_losses: np.ndarray
    names: tuple[str,...]


PRESETS={
 "Individual / Household":IntegratedScenario("Individual / Household",(
   RiskNode("Income interruption","Income",7000,1.4,"lognormal",.55),RiskNode("Property / vehicle loss","Property",3500,1.1,"gamma",.25),RiskNode("Emergency expense","Financial",4500,1.0,"gamma",.30),RiskNode("Investment drawdown","Market",5000,1.3,"lognormal",.60)),25000),
 "Solo Professional":IntegratedScenario("Solo Professional",(
   RiskNode("Client concentration","Revenue",18000,1.25,"lognormal",.60),RiskNode("Payment default","Credit",7000,1.0,"gamma",.45),RiskNode("Work interruption","Continuity",9000,1.15,"lognormal",.30),RiskNode("Market / reserve loss","Market",6000,1.2,"gamma",.55)),45000),
 "Growing Small Business":IntegratedScenario("Growing Small Business",(
   RiskNode("Revenue interruption","Revenue",60000,1.25,"lognormal",.65),RiskNode("Customer credit","Credit",42000,1.0,"gamma",.55),RiskNode("Operating disruption","Continuity",38000,1.15,"lognormal",.35),RiskNode("Input / market shock","Market",45000,1.1,"gamma",.60),RiskNode("Strategic miss","Strategic",50000,1.30,"lognormal",.50)),300000),
 "Mid-Market Company":IntegratedScenario("Mid-Market Company",(
   RiskNode("Demand shock","Strategic",3500000,1.2,"lognormal",.70),RiskNode("Credit loss","Credit",2200000,1.0,"gamma",.60),RiskNode("Production interruption","Continuity",2600000,1.15,"lognormal",.35),RiskNode("Input cost / FX","Market",3000000,1.1,"gamma",.65),RiskNode("Investment impairment","Strategic",1800000,1.35,"lognormal",.45)),13000000),
 "Large Organization":IntegratedScenario("Large Organization",(
   RiskNode("Macro revenue risk","Strategic",160000000,1.15,"lognormal",.75),RiskNode("Counterparty risk","Credit",90000000,1.0,"gamma",.62),RiskNode("Market / FX risk","Market",110000000,1.10,"gamma",.72),RiskNode("Continuity risk","Continuity",80000000,1.25,"lognormal",.40),RiskNode("Strategic investment risk","Strategic",120000000,1.35,"lognormal",.52),RiskNode("Liquidity event loss","Liquidity",70000000,1.10,"gamma",.58)),650000000),
}


def _ppf(node:RiskNode,u):
    node.validated(); m=node.mean_loss; cv=node.coefficient_of_variation
    if m==0:return np.zeros_like(u)
    if cv==0:return np.full_like(u,m,dtype=float)
    if node.distribution=='lognormal':
        sigma=np.sqrt(np.log1p(cv*cv));mu=np.log(m)-.5*sigma*sigma;return lognorm.ppf(u,s=sigma,scale=np.exp(mu))
    shape=1/(cv*cv);scale=m/shape;return gamma.ppf(u,a=shape,scale=scale)


def standalone_var95(node:RiskNode)->float:
    return float(_ppf(node,np.array([.95]))[0])


def simulate_integrated(risks,n_simulations=50000,seed=42,correlation_scale=1.0)->IntegratedResult:
    risks=[r.validated() for r in risks];rng=np.random.default_rng(seed);common=rng.standard_normal(n_simulations);cols=[]
    for r in risks:
        beta=min(max(r.common_factor_loading*float(correlation_scale),0),.98)
        z=beta*common+np.sqrt(1-beta*beta)*rng.standard_normal(n_simulations)
        u=np.clip(norm.cdf(z),1e-10,1-1e-10);cols.append(_ppf(r,u))
    components=np.column_stack(cols);return IntegratedResult(components.sum(axis=1),components,tuple(r.name for r in risks))


def summarize(result:IntegratedResult,risks,reserve:float)->dict[str,float]:
    v95=float(np.quantile(result.total_losses,.95));v99=float(np.quantile(result.total_losses,.99));es95=float(result.total_losses[result.total_losses>=v95].mean())
    standalone=sum(standalone_var95(r) for r in risks)
    return {"expected_loss":float(result.total_losses.mean()),"volatility":float(result.total_losses.std(ddof=1)),"var_95":v95,"var_99":v99,"es_95":es95,
            "reserve_breach_probability":float((result.total_losses>reserve).mean()),"sum_standalone_var95":standalone,"diversification_benefit_var95":float(standalone-v95)}


def tail_contributions(result:IntegratedResult,confidence=.95)->pd.DataFrame:
    v=np.quantile(result.total_losses,confidence);tail=result.component_losses[result.total_losses>=v].mean(axis=0);total=tail.sum()
    return pd.DataFrame({'risk':result.names,'tail_loss':tail,'tail_contribution':tail/total if total else 0}).sort_values('tail_contribution',ascending=False)


def dependency_comparison(scenario:IntegratedScenario,n=40000,seed=42)->pd.DataFrame:
    rows=[]
    for scale in (0,.25,.5,.75,1,1.25):
        r=simulate_integrated(scenario.risks,n,seed,scale);m=summarize(r,scenario.risks,scenario.reserve);rows.append({'correlation_scale':scale,**m})
    return pd.DataFrame(rows)


def independent_vs_dependent(scenario:IntegratedScenario,n=50000,seed=42):
    a=simulate_integrated(scenario.risks,n,seed,0);b=simulate_integrated(scenario.risks,n,seed,1);return summarize(a,scenario.risks,scenario.reserve),summarize(b,scenario.risks,scenario.reserve)
