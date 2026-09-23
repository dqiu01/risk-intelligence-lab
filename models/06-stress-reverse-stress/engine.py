from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import minimize, brentq


@dataclass(frozen=True)
class StressFactor:
    name: str
    max_adverse_change_pct: float
    linear_loss_at_max: float
    quadratic_loss_at_max: float = 0.0
    plausibility_weight: float = 1.0

    def validated(self):
        if self.max_adverse_change_pct <= 0 or self.linear_loss_at_max < 0 or self.quadratic_loss_at_max < 0 or self.plausibility_weight <= 0:
            raise ValueError(f"Invalid stress factor {self.name}")
        return self


@dataclass(frozen=True)
class StressModel:
    name: str
    risk_capacity: float
    factors: tuple[StressFactor,...]
    interaction_loss_full: float = 0.0


PRESETS={
 "Individual / Household":StressModel("Individual / Household",50000,(
   StressFactor("Income decline",50,32000,9000,1.0),StressFactor("Essential cost spike",40,15000,6000,1.2),StressFactor("Borrowing-cost shock",60,10000,5000,1.3),StressFactor("Asset-value decline",45,18000,8000,1.1)),12000),
 "Solo Professional":StressModel("Solo Professional",80000,(
   StressFactor("Client demand decline",60,50000,18000,1.0),StressFactor("Pricing pressure",30,28000,9000,1.1),StressFactor("Cost inflation",35,22000,8000,1.2),StressFactor("Collection deterioration",50,26000,11000,1.0)),18000),
 "Growing Small Business":StressModel("Growing Small Business",1200000,(
   StressFactor("Demand decline",45,650000,280000,1.0),StressFactor("Margin compression",30,520000,220000,1.1),StressFactor("Input-cost shock",40,430000,190000,1.2),StressFactor("Funding-cost shock",70,260000,140000,1.3),StressFactor("Customer concentration event",60,480000,250000,1.0)),350000),
 "Mid-Market Company":StressModel("Mid-Market Company",25000000,(
   StressFactor("Demand decline",35,13000000,6000000,1.0),StressFactor("Price compression",20,10000000,4500000,1.1),StressFactor("Input-cost inflation",30,9000000,5000000,1.1),StressFactor("Rate shock",80,5500000,3000000,1.3),StressFactor("Counterparty deterioration",70,8000000,4000000,1.2)),6500000),
 "Large Organization":StressModel("Large Organization",1000000000,(
   StressFactor("Global demand shock",30,480000000,260000000,1.0),StressFactor("Price/mix deterioration",18,360000000,180000000,1.1),StressFactor("Input basket shock",28,310000000,170000000,1.1),StressFactor("FX / rates shock",75,240000000,150000000,1.25),StressFactor("Credit deterioration",80,330000000,190000000,1.15),StressFactor("Strategic impairment",65,400000000,240000000,1.2)),280000000),
}


def loss_at(model:StressModel,x)->float:
    x=np.clip(np.asarray(x,dtype=float),0,1); fs=model.factors
    base=sum(f.linear_loss_at_max*x[i]+f.quadratic_loss_at_max*x[i]**2 for i,f in enumerate(fs))
    if len(fs)>1 and model.interaction_loss_full:
        pairs=[x[i]*x[j] for i in range(len(fs)) for j in range(i+1,len(fs))]
        base += model.interaction_loss_full*float(np.mean(pairs))
    return float(base)


def scenario_table(model:StressModel)->pd.DataFrame:
    rows=[]
    for name,level in [('Mild',.25),('Moderate',.50),('Severe',.75),('Extreme',1.0)]:
        x=np.full(len(model.factors),level); loss=loss_at(model,x)
        rows.append({'scenario':name,'normalized_stress':level,'modeled_loss':loss,'capacity_usage':loss/model.risk_capacity,'capacity_breached':loss>=model.risk_capacity})
    return pd.DataFrame(rows)


def reverse_stress(model:StressModel,capacity:float|None=None)->dict:
    cap=model.risk_capacity if capacity is None else float(capacity); n=len(model.factors)
    max_loss=loss_at(model,np.ones(n))
    if cap<=0:return {'success':True,'normalized_shocks':np.zeros(n),'loss':0.0,'distance':0.0,'capacity':cap}
    if max_loss<cap:return {'success':False,'normalized_shocks':np.ones(n),'loss':max_loss,'distance':np.nan,'capacity':cap}
    weights=np.array([f.plausibility_weight for f in model.factors])
    objective=lambda x: float(np.sum(weights*np.asarray(x)**2))
    constraint={'type':'ineq','fun':lambda x:loss_at(model,x)-cap}
    starts=[np.full(n,v) for v in (.2,.4,.6,.8,1.0)]
    best=None
    for start in starts:
        res=minimize(objective,start,method='SLSQP',bounds=[(0,1)]*n,constraints=[constraint],options={'ftol':1e-11,'maxiter':1000})
        if res.success and loss_at(model,res.x)>=cap*(1-1e-7):
            if best is None or res.fun<best.fun:best=res
    if best is None:return {'success':False,'normalized_shocks':np.ones(n),'loss':max_loss,'distance':np.nan,'capacity':cap}
    return {'success':True,'normalized_shocks':np.clip(best.x,0,1),'loss':loss_at(model,best.x),'distance':float(np.sqrt(best.fun)),'capacity':cap}


def reverse_stress_table(model:StressModel,capacity:float|None=None)->pd.DataFrame:
    r=reverse_stress(model,capacity); x=r['normalized_shocks']
    return pd.DataFrame({'factor':[f.name for f in model.factors],'normalized_shock':x,'adverse_change_pct':[x[i]*f.max_adverse_change_pct for i,f in enumerate(model.factors)]})


def single_factor_breakpoints(model:StressModel,capacity:float|None=None)->pd.DataFrame:
    cap=model.risk_capacity if capacity is None else float(capacity); rows=[]
    for i,f in enumerate(model.factors):
        def fn(x):return f.linear_loss_at_max*x+f.quadratic_loss_at_max*x*x-cap
        if fn(1)<0:x=np.nan
        else:x=brentq(fn,0,1)
        rows.append({'factor':f.name,'normalized_breakpoint':x,'adverse_change_pct':x*f.max_adverse_change_pct if np.isfinite(x) else np.nan})
    return pd.DataFrame(rows)


def two_factor_surface(model:StressModel,points=31):
    if len(model.factors)<2:raise ValueError('need two factors')
    grid=np.linspace(0,1,points); z=np.zeros((points,points)); zeros=np.zeros(len(model.factors))
    for i,a in enumerate(grid):
        for j,b in enumerate(grid):
            x=zeros.copy();x[0]=a;x[1]=b;z[j,i]=loss_at(model,x)
    return grid,grid,z
