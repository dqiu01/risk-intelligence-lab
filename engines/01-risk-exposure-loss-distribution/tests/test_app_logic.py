import pandas as pd

import app


def test_default_scenario_table_parses():
    frame = app.scenario_to_table(app.DEFAULT_SCENARIO)
    risks = app.parse_risk_table(frame)
    assert len(risks) == len(frame)


def test_ui_analysis_returns_all_outputs():
    s = app.SCENARIOS[app.DEFAULT_SCENARIO]
    outputs = app.run_analysis_ui(
        app.DEFAULT_SCENARIO,
        s.annual_income_revenue,
        s.reserve,
        s.risk_tolerance,
        app.scenario_to_table(app.DEFAULT_SCENARIO),
        10_000,
        42,
        True,
        "Base",
        0,
        0,
        0,
        [],
        s.reserve,
        95,
    )
    assert len(outputs) == 9
    assert "Expected loss" in outputs[0]
    assert isinstance(outputs[5], pd.DataFrame)
    assert isinstance(outputs[6], pd.DataFrame)


def test_app_builds():
    ui = app.build_app()
    assert ui is not None
