from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Asset:
    name: str
    weight: float
    annual_return: float
    annual_volatility: float

    def validated(self):
        if self.weight < 0 or self.annual_volatility < 0:
            raise ValueError("weights and volatility must be non-negative")
        return self


@dataclass(frozen=True)
class PortfolioScenario:
    name: str
    portfolio_value: float
    assets: tuple[Asset, ...]
    correlation: float = 0.25
    df: float = 6.0
    horizon_days: int = 10

    def validated(self):
        if self.portfolio_value <= 0 or self.horizon_days < 1 or self.df <= 2:
            raise ValueError("invalid portfolio configuration")
        if not -0.2 <= self.correlation < 1:
            raise ValueError("correlation out of supported range")
        for a in self.assets: a.validated()
        if sum(a.weight for a in self.assets) <= 0:
            raise ValueError("at least one positive weight required")
        return self


@dataclass(frozen=True)
class MarketResult:
    losses: np.ndarray
    returns: np.ndarray
    max_drawdowns: np.ndarray
    asset_linear_losses: np.ndarray
    weights: np.ndarray
    asset_names: tuple[str, ...]


PRESETS = {
    "Individual Growth Portfolio": PortfolioScenario("Individual Growth Portfolio",250000,(
        Asset("US Equity",.45,.07,.18),Asset("Bonds",.25,.035,.06),Asset("International Equity",.20,.07,.20),Asset("Cash",.10,.03,.01)),.25,6,10),
    "Solo Professional Reserve": PortfolioScenario("Solo Professional Reserve",150000,(
        Asset("Cash",.35,.03,.01),Asset("Short Bonds",.35,.035,.045),Asset("Broad Equity",.20,.07,.18),Asset("Gold",.10,.04,.16)),.15,7,10),
    "Small Business Treasury": PortfolioScenario("Small Business Treasury",2000000,(
        Asset("Cash",.30,.03,.01),Asset("Treasury Bonds",.35,.035,.055),Asset("Investment Grade Credit",.20,.045,.08),Asset("Equity Reserve",.15,.07,.19)),.30,6,10),
    "Institutional Multi-Asset": PortfolioScenario("Institutional Multi-Asset",100000000,(
        Asset("Global Equity",.35,.075,.19),Asset("Government Bonds",.25,.035,.07),Asset("Credit",.15,.05,.10),Asset("Commodities",.10,.04,.18),Asset("Alternatives",.15,.065,.14)),.35,5,20),
    "Large Organization Treasury": PortfolioScenario("Large Organization Treasury",750000000,(
        Asset("Cash",.20,.03,.01),Asset("Government Bonds",.30,.035,.065),Asset("Credit",.20,.05,.095),Asset("Equity",.15,.07,.19),Asset("Commodity Hedge",.15,.035,.17)),.28,6,10),
}


def normalized_weights(assets):
    w=np.array([a.weight for a in assets],dtype=float)
    total=w.sum()
    if total <= 0: raise ValueError("weights must sum positive")
    return w/total


def correlation_matrix(n:int,rho:float)->np.ndarray:
    low=-1/(n-1)+1e-6 if n>1 else 0
    rho=max(rho,low)
    m=np.full((n,n),rho,dtype=float); np.fill_diagonal(m,1.0)
    return m


def parametric_annual_volatility(s:PortfolioScenario, correlation:float|None=None)->float:
    s.validated(); rho=s.correlation if correlation is None else correlation
    w=normalized_weights(s.assets); vols=np.array([a.annual_volatility for a in s.assets])
    cov=np.outer(vols,vols)*correlation_matrix(len(w),rho)
    return float(np.sqrt(w@cov@w))


def simulate_market(s:PortfolioScenario,n_simulations:int=50000,seed:int=42,correlation:float|None=None,horizon_days:int|None=None)->MarketResult:
    s.validated(); rng=np.random.default_rng(seed)
    rho=s.correlation if correlation is None else float(correlation)
    days=s.horizon_days if horizon_days is None else int(horizon_days)
    n_assets=len(s.assets); corr=correlation_matrix(n_assets,rho); chol=np.linalg.cholesky(corr)
    w=normalized_weights(s.assets)
    ann_ret=np.array([a.annual_return for a in s.assets]); ann_vol=np.array([a.annual_volatility for a in s.assets])
    mu=ann_ret/252; sigma=ann_vol/np.sqrt(252)
    normals=rng.standard_normal((n_simulations,days,n_assets)) @ chol.T
    chi=rng.chisquare(s.df,size=(n_simulations,days,1))
    tdraw=normals*np.sqrt((s.df-2)/chi)
    asset_r=mu+sigma*tdraw
    asset_r=np.clip(asset_r,-.95,None)
    port_daily=asset_r@w
    wealth=np.cumprod(1+port_daily,axis=1)
    terminal=wealth[:,-1]-1
    losses=-s.portfolio_value*terminal
    running_max=np.maximum.accumulate(np.column_stack([np.ones(n_simulations),wealth]),axis=1)[:,1:]
    dd=1-wealth/running_max
    max_dd=dd.max(axis=1)
    asset_linear_losses=-s.portfolio_value*(asset_r.sum(axis=1)*w)
    return MarketResult(losses,terminal,max_dd,asset_linear_losses,w,tuple(a.name for a in s.assets))


def summarize(r:MarketResult)->dict[str,float]:
    v95=float(np.quantile(r.losses,.95)); v99=float(np.quantile(r.losses,.99))
    return {"expected_pnl":float(-r.losses.mean()),"var_95":v95,"var_99":v99,
            "es_95":float(r.losses[r.losses>=v95].mean()),"es_99":float(r.losses[r.losses>=v99].mean()),
            "loss_probability":float((r.losses>0).mean()),"p95_max_drawdown":float(np.quantile(r.max_drawdowns,.95))}


def tail_contributions(r:MarketResult,confidence=.95)->pd.DataFrame:
    threshold=np.quantile(r.losses,confidence); mask=r.losses>=threshold
    c=r.asset_linear_losses[mask].mean(axis=0); total=c.sum()
    share=c/total if abs(total)>1e-12 else np.zeros_like(c)
    return pd.DataFrame({"asset":r.asset_names,"tail_loss":c,"tail_contribution":share}).sort_values("tail_contribution",ascending=False)


def stress_test(s:PortfolioScenario,shocks:dict[str,float]|None=None)->pd.DataFrame:
    default={a.name:-2*a.annual_volatility/np.sqrt(12) for a in s.assets}
    shocks=default if shocks is None else shocks
    w=normalized_weights(s.assets)
    rows=[]; total=0.0
    for wi,a in zip(w,s.assets):
        shock=float(shocks.get(a.name,0)); pnl=s.portfolio_value*wi*shock; total+=pnl
        rows.append({"asset":a.name,"shock_pct":100*shock,"pnl":pnl})
    rows.append({"asset":"TOTAL","shock_pct":np.nan,"pnl":total})
    return pd.DataFrame(rows)
