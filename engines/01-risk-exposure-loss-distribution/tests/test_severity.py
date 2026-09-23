import numpy as np

from risk_model.schemas import RiskExposure
from risk_model.severity import analytical_severity_mean, calibrate_severity, sample_severity


def make_risk(dist="lognormal"):
    return RiskExposure(name="Test", category="Financial", annual_frequency=2.0, typical_loss=10_000, large_loss=30_000, extreme_loss=100_000, severity_distribution=dist)


def test_supported_distributions_are_nonnegative_and_capped():
    rng = np.random.default_rng(42)
    for dist in ["lognormal", "gamma", "triangular"]:
        risk = make_risk(dist)
        values = sample_severity(rng, risk, 50_000)
        assert np.all(values >= 0)
        assert values.max() <= risk.extreme_loss + 1e-9
        assert values.mean() > 0


def test_control_effectiveness_reduces_mean_severity():
    base = make_risk("lognormal")
    controlled = RiskExposure(**{**base.__dict__, "control_effectiveness": 0.40})
    assert analytical_severity_mean(controlled) < analytical_severity_mean(base)


def test_calibration_uses_requested_distribution():
    assert calibrate_severity(make_risk("gamma")).distribution == "gamma"
    assert calibrate_severity(make_risk("triangular")).distribution == "triangular"
