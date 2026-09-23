from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Driver:
    name: str
    base_value: float
    volatility_pct: float
    impact_per_1pct: float
    systemic_loading: float = 0.4

    def validated(self):
        if self.volatility_pct < 0 or not 0 <= self.systemic_loading <= 1:
            raise ValueError(f"Invalid driver {self.name}")
        return self


@dataclass(frozen=True)
class ScenarioModel:
    name: str
    base_outcome: float
    target: float
    drivers: tuple[Driver,...]
    downside_convexity: float = 0.0


@dataclass(frozen=True)
class ScenarioResult:
    outcomes: np.ndarray
    driver_moves_pct: np.ndarray
    driver_names: tuple[str,...]
    common_factor: np.ndarray


PRESETS={
 "Individual / Household":ScenarioModel("Individual / Household",22000,10000,(
   Driver("Employment income",120000,8,1150,.55),Driver("Essential living cost",70000,10,-700,.35),Driver("Borrowing cost",8000,18,-180,.50),Driver("Investment income",10000,25,120,.60)),1200),
 "Solo Professional":ScenarioModel("Solo Professional",85000,55000,(
   Driver("Client demand",180000,15,1150,.60),Driver("Average pricing",1,8,900,.35),Driver("Operating cost",85000,10,-700,.30),Driver("Collection quality",1,12,500,.45)),3500),
 "Growing Small Business":ScenarioModel("Growing Small Business",650000,400000,(
   Driver("Demand",5000000,12,42000,.65),Driver("Gross margin",.45,8,32000,.40),Driver("Fixed operating cost",1600000,10,-26000,.30),Driver("Financing cost",250000,20,-9000,.55),Driver("Price realization",1,6,28000,.45)),50000),
 "Mid-Market Company":ScenarioModel("Mid-Market Company",18000000,12000000,(
   Driver("Unit demand",150000000,10,1100000,.65),Driver("Selling price",1,6,1400000,.55),Driver("Input cost",60000000,12,-900000,.60),Driver("Labor cost",35000000,7,-700000,.35),Driver("Interest rate burden",6000000,18,-350000,.60)),1500000),
 "Large Organization":ScenarioModel("Large Organization",900000000,650000000,(
   Driver("Global demand",5000000000,8,65000000,.75),Driver("Pricing",1,5,80000000,.55),Driver("Input basket",2100000000,10,-52000000,.65),Driver("FX translation",1,9,28000000,.70),Driver("Funding cost",300000000,15,-18000000,.60),Driver("Product mix",1,7,35000000,.45)),90000000),
}


def simulate(model:ScenarioModel,n_simulations=50000,seed=42,systemic_stress=0.0)->ScenarioResult:
    if n_simulations<=0:raise ValueError('n_simulations must be positive')
    rng=np.random.default_rng(seed); common=rng.standard_normal(n_simulations)+float(systemic_stress)
    moves=[]
    for d in model.drivers:
        d.validated(); eps=rng.standard_normal(n_simulations); z=d.systemic_loading*common+np.sqrt(1-d.systemic_loading**2)*eps
        moves.append(d.volatility_pct*z)
    moves=np.column_stack(moves)
    impacts=np.array([d.impact_per_1pct for d in model.drivers])
    outcomes=model.base_outcome+moves@impacts
    if model.downside_convexity:
        outcomes -= model.downside_convexity*np.minimum(common,0)**2
    return ScenarioResult(outcomes,moves,tuple(d.name for d in model.drivers),common)


def summarize(result:ScenarioResult,target:float,base_outcome:float)->dict[str,float]:
    p05=float(np.quantile(result.outcomes,.05)); misses=result.outcomes<target
    shortfall=np.maximum(target-result.outcomes,0)
    return {"expected_outcome":float(result.outcomes.mean()),"median_outcome":float(np.median(result.outcomes)),"p05_outcome":p05,"p95_outcome":float(np.quantile(result.outcomes,.95)),
            "target_miss_probability":float(misses.mean()),"expected_shortfall_below_target":float(shortfall[misses].mean()) if misses.any() else 0.0,"outcome_at_risk_95":float(base_outcome-p05)}


def driver_importance(result:ScenarioResult)->pd.DataFrame:
    rows=[]
    for i,name in enumerate(result.driver_names):
        corr=np.corrcoef(result.driver_moves_pct[:,i],result.outcomes)[0,1]
        rows.append({"driver":name,"outcome_correlation":corr,"absolute_importance":abs(corr)})
    return pd.DataFrame(rows).sort_values('absolute_importance',ascending=False)


def stress_table(model:ScenarioModel)->pd.DataFrame:
    rows=[]
    for label,sigma in [('Mild adverse',.75),('Moderate adverse',1.5),('Severe adverse',2.5),('Extreme adverse',3.5)]:
        impact=0.0
        for d in model.drivers:
            adverse_move=-np.sign(d.impact_per_1pct)*d.volatility_pct*sigma
            impact += adverse_move*d.impact_per_1pct
        outcome=model.base_outcome+impact-model.downside_convexity*sigma**2
        rows.append({'scenario':label,'adverse_sigma':sigma,'modeled_outcome':outcome,'change_vs_base':outcome-model.base_outcome,'target_breached':outcome<model.target})
    return pd.DataFrame(rows)
