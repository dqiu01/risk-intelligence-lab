import numpy as np
from engine import PRESETS, simulate_market, summarize, tail_contributions, parametric_annual_volatility, stress_test

def test_reproducible():
    s=PRESETS['Individual Growth Portfolio']; a=simulate_market(s,5000,1); b=simulate_market(s,5000,1); assert np.array_equal(a.losses,b.losses)

def test_tail_ordering():
    m=summarize(simulate_market(PRESETS['Individual Growth Portfolio'],20000,42)); assert m['es_95']>=m['var_95']; assert m['var_99']>=m['var_95']

def test_contributions_reconcile():
    c=tail_contributions(simulate_market(PRESETS['Small Business Treasury'],20000,3)); assert np.isclose(c.tail_contribution.sum(),1,atol=.03)

def test_higher_correlation_increases_parametric_vol():
    s=PRESETS['Institutional Multi-Asset']; assert parametric_annual_volatility(s,.7)>parametric_annual_volatility(s,.0)

def test_stress_has_total():
    df=stress_test(PRESETS['Large Organization Treasury']); assert df.iloc[-1].asset=='TOTAL'; assert df.iloc[-1].pnl<0
