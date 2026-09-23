import numpy as np

from risk_model.metrics import exceedance_probability, expected_shortfall, required_reserve, risk_contributions, summarize_losses, value_at_risk
from risk_model.schemas import RiskExposure
from risk_model.simulation import simulate_portfolio


def portfolio():
    risks = [
        RiskExposure("A", "Credit", 2.0, 10_000, 30_000, 100_000, systemic_sensitivity=0.3),
        RiskExposure("B", "Strategic", 0.8, 25_000, 80_000, 250_000, severity_distribution="gamma", systemic_sensitivity=0.5),
    ]
    return simulate_portfolio(risks, 40_000, seed=42)


def test_tail_metrics_have_expected_ordering():
    result = portfolio()
    v95 = value_at_risk(result.total_losses, 0.95)
    v99 = value_at_risk(result.total_losses, 0.99)
    es95 = expected_shortfall(result.total_losses, 0.95)
    assert v99 >= v95
    assert es95 >= v95


def test_required_reserve_is_quantile():
    result = portfolio()
    reserve = required_reserve(result.total_losses, 0.95)
    assert exceedance_probability(result.total_losses, reserve) <= 0.051


def test_contributions_sum_to_one():
    result = portfolio()
    c = risk_contributions(result)
    assert np.isclose(c["expected_contribution"].sum(), 1.0)
    assert np.isclose(c["tail_contribution"].sum(), 1.0)


def test_summary_probabilities_are_bounded():
    result = portfolio()
    m = summarize_losses(result, reserve=80_000, risk_tolerance=150_000)
    assert 0 <= m.reserve_breach_probability <= 1
    assert 0 <= m.tolerance_breach_probability <= 1
