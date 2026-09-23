from __future__ import annotations

from dataclasses import replace

from .schemas import MitigationAction, RiskExposure


def apply_mitigations(
    risks: list[RiskExposure] | tuple[RiskExposure, ...],
    mitigations: list[MitigationAction] | tuple[MitigationAction, ...],
    selected_names: set[str] | None = None,
) -> tuple[list[RiskExposure], float]:
    selected_names = selected_names or {m.name for m in mitigations}
    actions_by_risk: dict[str, list[MitigationAction]] = {}
    total_cost = 0.0
    for action in mitigations:
        action.validated()
        if action.name not in selected_names:
            continue
        actions_by_risk.setdefault(action.risk_name, []).append(action)
        total_cost += action.annual_cost

    output: list[RiskExposure] = []
    for risk in risks:
        updated = risk
        for action in actions_by_risk.get(risk.name, []):
            updated = updated.with_mitigation(action.frequency_reduction, action.severity_reduction)
        output.append(replace(updated))
    return output, total_cost
