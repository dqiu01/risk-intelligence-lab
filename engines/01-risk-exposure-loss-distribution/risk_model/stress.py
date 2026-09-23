from __future__ import annotations

from .schemas import RiskExposure


def apply_global_stress(
    risks: list[RiskExposure] | tuple[RiskExposure, ...],
    frequency_shock_pct: float = 0.0,
    severity_shock_pct: float = 0.0,
    control_degradation_pct: float = 0.0,
) -> list[RiskExposure]:
    if frequency_shock_pct < -100 or severity_shock_pct < -100:
        raise ValueError("Frequency and severity shocks cannot reduce below -100%.")
    if not 0 <= control_degradation_pct <= 100:
        raise ValueError("control_degradation_pct must be between 0 and 100.")

    frequency_multiplier = 1.0 + frequency_shock_pct / 100.0
    severity_multiplier = 1.0 + severity_shock_pct / 100.0
    degradation = control_degradation_pct / 100.0

    stressed: list[RiskExposure] = []
    for risk in risks:
        r = risk.with_stress(frequency_multiplier, severity_multiplier)
        r = type(r)(**{**r.__dict__, "control_effectiveness": r.control_effectiveness * (1.0 - degradation)})
        stressed.append(r)
    return stressed


STRESS_PRESETS = {
    "Base": (0.0, 0.0, 0.0),
    "Mild slowdown": (20.0, 10.0, 5.0),
    "Severe downturn": (60.0, 35.0, 20.0),
    "Control failure": (10.0, 15.0, 75.0),
    "Compound shock": (80.0, 50.0, 40.0),
}
