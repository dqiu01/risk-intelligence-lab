from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass(frozen=True)
class Option:
    name: str
    expected_benefit_rate: float
    risk_rate: float
    max_allocation: float

    def validated(self):
        if self.max_allocation < 0 or self.risk_rate < 0:
            raise ValueError(f"Invalid option {self.name}")
        return self


@dataclass(frozen=True)
class OptimizationScenario:
    name: str
    budget: float
    risk_limit: float
    options: tuple[Option,...]
    correlation: float = 0.20


PRESETS={
 "Individual / Household":OptimizationScenario("Individual / Household",50000,5500,(
   Option("Emergency reserve",.03,.005,25000),Option("Debt payoff",.065,.01,20000),Option("Short bonds",.04,.05,30000),Option("Diversified equity",.08,.18,30000)),.10),
 "Solo Professional":OptimizationScenario("Solo Professional",100000,12000,(
   Option("Cash reserve",.03,.01,40000),Option("Client acquisition",.18,.28,45000),Option("Equipment / automation",.14,.18,50000),Option("Skill / product development",.16,.22,40000)),.20),
 "Growing Small Business":OptimizationScenario("Growing Small Business",2000000,260000,(
   Option("Liquidity reserve",.035,.015,700000),Option("Growth marketing",.20,.30,700000),Option("Process automation",.15,.17,900000),Option("Capacity expansion",.17,.24,1000000),Option("Risk-control program",.11,.08,500000)),.22),
 "Mid-Market Company":OptimizationScenario("Mid-Market Company",50000000,5500000,(
   Option("Liquidity buffer",.035,.012,15000000),Option("Core expansion",.16,.20,22000000),Option("Automation program",.13,.14,18000000),Option("New market entry",.21,.32,18000000),Option("Resilience program",.10,.07,12000000)),.25),
 "Large Organization":OptimizationScenario("Large Organization",500000000,48000000,(
   Option("Liquidity / treasury",.035,.012,150000000),Option("Core capex",.14,.16,220000000),Option("Digital transformation",.17,.22,160000000),Option("Strategic growth",.20,.30,180000000),Option("Resilience / hedging",.09,.06,120000000),Option("R&D portfolio",.18,.27,150000000)),.28),
}


def covariance_matrix(options,correlation):
    n=len(options); low=-1/(n-1)+1e-6 if n>1 else 0; rho=max(float(correlation),low)
    corr=np.full((n,n),rho);np.fill_diagonal(corr,1);risks=np.array([o.risk_rate for o in options]);return np.outer(risks,risks)*corr


def portfolio_metrics(x,scenario:OptimizationScenario):
    x=np.asarray(x,dtype=float);rates=np.array([o.expected_benefit_rate for o in scenario.options]);cov=covariance_matrix(scenario.options,scenario.correlation)
    benefit=float(rates@x);risk=float(np.sqrt(max(x@cov@x,0)));return benefit,risk,float(x.sum())


def optimize_allocation(scenario:OptimizationScenario,risk_limit:float|None=None,risk_aversion:float=0.0):
    for o in scenario.options:o.validated()
    limit=scenario.risk_limit if risk_limit is None else float(risk_limit);n=len(scenario.options);caps=np.array([o.max_allocation for o in scenario.options])
    x0=np.minimum(caps,scenario.budget/max(n,1));
    if x0.sum()>scenario.budget:x0*=scenario.budget/x0.sum()
    def objective(x):
        b,r,_=portfolio_metrics(x,scenario);return -(b-float(risk_aversion)*r)
    cons=[{'type':'ineq','fun':lambda x:scenario.budget-np.sum(x)},{'type':'ineq','fun':lambda x:limit-portfolio_metrics(x,scenario)[1]}]
    res=minimize(objective,x0,method='SLSQP',bounds=[(0,c) for c in caps],constraints=cons,options={'ftol':1e-9,'maxiter':2000})
    if not res.success:
        zero=np.zeros(n);return {'success':False,'allocation':zero,'expected_benefit':0.0,'risk':0.0,'spent':0.0,'message':res.message}
    b,r,spent=portfolio_metrics(res.x,scenario);return {'success':True,'allocation':np.clip(res.x,0,caps),'expected_benefit':b,'risk':r,'spent':spent,'message':res.message}


def allocation_table(scenario,result):
    x=result['allocation'];cov=covariance_matrix(scenario.options,scenario.correlation);risk=max(result['risk'],1e-12);mrc=x*(cov@x)/risk
    return pd.DataFrame({'option':[o.name for o in scenario.options],'allocation':x,'allocation_pct_budget':x/scenario.budget,'expected_benefit':[x[i]*o.expected_benefit_rate for i,o in enumerate(scenario.options)],'risk_contribution':mrc,'risk_contribution_pct':mrc/risk})


def efficient_frontier(scenario,points=24):
    max_limit=max(scenario.risk_limit*1.5,1e-9);limits=np.linspace(max_limit/points,max_limit,points);rows=[]
    for limit in limits:
        r=optimize_allocation(scenario,limit,0);rows.append({'risk_limit':limit,'realized_risk':r['risk'],'expected_benefit':r['expected_benefit'],'spent':r['spent']})
    return pd.DataFrame(rows)
