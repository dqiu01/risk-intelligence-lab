from risk_model.analysis import analyze
from risk_model.mitigation import apply_mitigations
from risk_model.schemas import MitigationAction, RiskExposure
from risk_model.stress import apply_global_stress


def base_risks():
    return [
        RiskExposure("Default", "Credit", 4.0, 20_000, 60_000, 180_000, systemic_sensitivity=0.4),
        RiskExposure("Interruption", "Revenue", 1.0, 60_000, 180_000, 500_000, systemic_sensitivity=0.6),
    ]


def test_mitigation_reduces_expected_and_tail_loss():
    risks = base_risks()
    action = MitigationAction("Credit controls", "Default", 10_000, frequency_reduction=0.4, severity_reduction=0.2)
    mitigated, cost = apply_mitigations(risks, [action], {"Credit controls"})
    base = analyze(risks, 300_000, 500_000, 50_000, 42)
    alt = analyze(mitigated, 300_000, 500_000, 50_000, 42)
    assert cost == 10_000
    assert alt.metrics.expected_loss < base.metrics.expected_loss
    assert alt.metrics.es_95 < base.metrics.es_95


def test_stress_increases_expected_loss():
    risks = base_risks()
    stressed = apply_global_stress(risks, frequency_shock_pct=50, severity_shock_pct=30, control_degradation_pct=0)
    base = analyze(risks, 300_000, 500_000, 40_000, 9)
    alt = analyze(stressed, 300_000, 500_000, 40_000, 9)
    assert alt.metrics.expected_loss > base.metrics.expected_loss
