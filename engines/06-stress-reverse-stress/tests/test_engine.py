import numpy as np
from engine import PRESETS,loss_at,scenario_table,reverse_stress,reverse_stress_table

def test_loss_monotonic_on_uniform_stress():
 m=PRESETS['Growing Small Business'];assert loss_at(m,np.full(len(m.factors),.8))>loss_at(m,np.full(len(m.factors),.4))
def test_reverse_stress_reaches_capacity():
 m=PRESETS['Growing Small Business'];r=reverse_stress(m);assert r['success'];assert r['loss']>=m.risk_capacity*(1-1e-6);assert (r['normalized_shocks']>=0).all() and (r['normalized_shocks']<=1).all()
def test_lower_capacity_not_farther():
 m=PRESETS['Mid-Market Company'];a=reverse_stress(m,m.risk_capacity*.7);b=reverse_stress(m,m.risk_capacity);assert a['distance']<=b['distance']+1e-6
def test_forward_scenarios_ordered():
 m=PRESETS['Individual / Household'];d=scenario_table(m);assert d.modeled_loss.is_monotonic_increasing
def test_impossible_threshold():
 m=PRESETS['Solo Professional'];r=reverse_stress(m,loss_at(m,np.ones(len(m.factors)))*1.1);assert not r['success']
