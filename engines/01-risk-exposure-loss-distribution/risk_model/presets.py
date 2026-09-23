from __future__ import annotations

from pathlib import Path

import yaml

from .schemas import MitigationAction, RiskExposure, ScenarioConfig


def load_scenario(path: str | Path) -> ScenarioConfig:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    risks = tuple(RiskExposure(**item) for item in data.get("risks", []))
    mitigations = tuple(MitigationAction(**item) for item in data.get("mitigations", []))
    return ScenarioConfig(
        name=data["name"],
        annual_income_revenue=float(data["annual_income_revenue"]),
        reserve=float(data["reserve"]),
        risk_tolerance=float(data["risk_tolerance"]),
        risks=risks,
        mitigations=mitigations,
    ).validated()


def load_all_scenarios(directory: str | Path) -> dict[str, ScenarioConfig]:
    directory = Path(directory)
    scenarios: dict[str, ScenarioConfig] = {}
    for path in sorted(directory.glob("*.yaml")):
        scenario = load_scenario(path)
        scenarios[scenario.name] = scenario
    return scenarios
