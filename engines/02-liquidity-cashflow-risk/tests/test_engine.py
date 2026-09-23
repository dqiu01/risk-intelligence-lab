import numpy as np
from engine import PRESETS, simulate_liquidity, summarize, compare_actions


def test_reproducible():
    s=PRESETS["Growing Small Business"]
    a=simulate_liquidity(s,5000,7).cash_paths
    b=simulate_liquidity(s,5000,7).cash_paths
    assert np.array_equal(a,b)


def test_metrics_bounded():
    s=PRESETS["Solo Professional"]
    m=summarize(simulate_liquidity(s,10000,42),s)
    assert 0 <= m["liquidity_breach_probability"] <= 1
    assert 0 <= m["insolvency_probability"] <= 1
    assert m["required_additional_buffer_95"] >= 0


def test_adverse_shock_worsens_liquidity():
    s=PRESETS["Growing Small Business"]
    base=summarize(simulate_liquidity(s,30000,42),s)
    bad=summarize(simulate_liquidity(s,30000,42,income_shock_pct=-20,cost_shock_pct=15),s)
    assert bad["expected_ending_cash"] < base["expected_ending_cash"]
    assert bad["liquidity_breach_probability"] > base["liquidity_breach_probability"]


def test_action_table():
    s=PRESETS["Growing Small Business"]
    df=compare_actions(s,10000,42)
    assert len(df)==5
    assert df.loc[df.action=="Add 25% reserve","liquidity_breach_probability"].iloc[0] <= df.loc[df.action=="Current","liquidity_breach_probability"].iloc[0]
