import numpy as np
from engine import PRESETS,optimize_allocation,allocation_table,efficient_frontier

def test_constraints_respected():
 s=PRESETS['Growing Small Business'];r=optimize_allocation(s);assert r['success'];assert r['spent']<=s.budget+1;assert r['risk']<=s.risk_limit+1
def test_caps_respected():
 s=PRESETS['Solo Professional'];r=optimize_allocation(s);assert all(x<=o.max_allocation+1 for x,o in zip(r['allocation'],s.options))
def test_more_risk_capacity_not_reduce_optimal_benefit():
 s=PRESETS['Mid-Market Company'];a=optimize_allocation(s,s.risk_limit*.6);b=optimize_allocation(s,s.risk_limit*1.2);assert b['expected_benefit']+1>=a['expected_benefit']
def test_risk_contributions_reconcile():
 s=PRESETS['Large Organization'];r=optimize_allocation(s);t=allocation_table(s,r);assert np.isclose(t.risk_contribution.sum(),r['risk'],rtol=1e-4,atol=1)
def test_frontier_generated():
 s=PRESETS['Individual / Household'];f=efficient_frontier(s,10);assert len(f)==10;assert (f.realized_risk<=f.risk_limit+1).all()
