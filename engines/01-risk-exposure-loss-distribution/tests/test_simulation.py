import numpy as np

from risk_model.schemas import RiskExposure
from risk_model.severity import analytical_severity_mean
from risk_model.simulation import simulate_portfolio


def base_risk(**overrides):
    data = dict(name="Default", category="Credit", annual_frequency=3.0, typical_loss=10_000, large_loss=25_000, extreme_loss=80_000, severity_distribution="lognormal", frequency_distribution="poisson", control_effectiveness=0.0, systemic_sensitivity=0.0)
    data.update(overrides)
    return RiskExposure(**data)


def test_simulation_is_reproducible():
    risk = base_risk()
    a = simulate_portfolio([risk], 10_000, seed=123)
    b = simulate_portfolio([risk], 10_000, seed=123)
    assert np.array_equal(a.total_losses, b.total_losses)


def test_poisson_expected_loss_matches_analytical_mean():
    risk = base_risk()
    result = simulate_portfolio([risk], 100_000, seed=7, dependency_enabled=False)
    analytical = risk.annual_frequency * analytical_severity_mean(risk)
    relative_error = abs(result.total_losses.mean() - analytical) / analytical
    assert relative_error < 0.025


def test_zero_frequency_produces_zero_loss():
    risk = base_risk(annual_frequency=0.0)
    result = simulate_portfolio([risk], 2_000, seed=1)
    assert np.all(result.total_losses == 0)


def test_dependency_can_induce_positive_loss_correlation():
    a = base_risk(name="A", systemic_sensitivity=0.8)
    b = base_risk(name="B", systemic_sensitivity=0.8)
    result = simulate_portfolio([a, b], 30_000, seed=10, dependency_enabled=True)
    assert result.risk_losses.corr().iloc[0, 1] > 0.05


def test_negative_binomial_frequency_runs():
    risk = base_risk(frequency_distribution="negative_binomial", nb_dispersion=1.5)
    result = simulate_portfolio([risk], 5_000, seed=11)
    assert result.total_losses.shape == (5_000,)
    assert result.event_counts.iloc[:, 0].mean() > 0
