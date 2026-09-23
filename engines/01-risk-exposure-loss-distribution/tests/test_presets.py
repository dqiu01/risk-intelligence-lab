from pathlib import Path

from risk_model.presets import load_all_scenarios


def test_all_presets_load_and_validate():
    scenarios = load_all_scenarios(Path(__file__).resolve().parents[1] / "scenarios")
    assert len(scenarios) >= 6
    for scenario in scenarios.values():
        assert scenario.annual_income_revenue > 0
        assert len(scenario.risks) >= 3


def test_all_presets_can_simulate():
    from risk_model.analysis import analyze
    scenarios = load_all_scenarios(Path(__file__).resolve().parents[1] / "scenarios")
    for scenario in scenarios.values():
        result = analyze(scenario.risks, scenario.reserve, scenario.risk_tolerance, 2_000, 123)
        assert result.metrics.expected_loss >= 0
        assert result.metrics.es_95 >= result.metrics.var_95
