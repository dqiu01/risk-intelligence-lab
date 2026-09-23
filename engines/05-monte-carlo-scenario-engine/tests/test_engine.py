import numpy as np
from engine import PRESETS,simulate,summarize,driver_importance,stress_table

def test_reproducible():
 m=PRESETS['Growing Small Business'];a=simulate(m,5000,42);b=simulate(m,5000,42);assert np.array_equal(a.outcomes,b.outcomes)
def test_metrics():
 m=PRESETS['Solo Professional'];s=summarize(simulate(m,20000,1),m.target,m.base_outcome);assert 0<=s['target_miss_probability']<=1;assert s['p95_outcome']>=s['p05_outcome']
def test_adverse_systemic_stress_reduces_outcome_for_default_presets():
 m=PRESETS['Growing Small Business'];base=simulate(m,30000,5,0).outcomes.mean();bad=simulate(m,30000,5,-2).outcomes.mean();assert bad<base
def test_importance_bounded():
 m=PRESETS['Mid-Market Company'];d=driver_importance(simulate(m,20000,3));assert (d.absolute_importance<=1.000001).all()
def test_stress_table_worsens():
 m=PRESETS['Large Organization'];d=stress_table(m);assert d.modeled_outcome.iloc[-1]<d.modeled_outcome.iloc[0]
