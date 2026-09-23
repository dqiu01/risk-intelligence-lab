from __future__ import annotations

from pathlib import Path

import gradio as gr
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from risk_model import (
    STRESS_PRESETS,
    RiskExposure,
    analyze,
    apply_global_stress,
    apply_mitigations,
    decision_interpretation,
    exceedance_curve,
    load_all_scenarios,
    required_reserve,
)

HERE = Path(__file__).resolve().parent
SCENARIOS = load_all_scenarios(HERE / "scenarios")
DEFAULT_SCENARIO = "Growing Small Business"

RISK_COLUMNS = [
    "name", "category", "annual_frequency", "typical_loss", "large_loss",
    "extreme_loss", "severity_distribution", "frequency_distribution",
    "control_effectiveness_pct", "systemic_sensitivity",
]


def scenario_to_table(name: str) -> pd.DataFrame:
    rows = []
    for r in SCENARIOS[name].risks:
        rows.append({
            "name": r.name,
            "category": r.category,
            "annual_frequency": r.annual_frequency,
            "typical_loss": r.typical_loss,
            "large_loss": r.large_loss,
            "extreme_loss": r.extreme_loss,
            "severity_distribution": r.severity_distribution,
            "frequency_distribution": r.frequency_distribution,
            "control_effectiveness_pct": 100 * r.control_effectiveness,
            "systemic_sensitivity": r.systemic_sensitivity,
        })
    return pd.DataFrame(rows, columns=RISK_COLUMNS)


def parse_risk_table(frame) -> list[RiskExposure]:
    if not isinstance(frame, pd.DataFrame):
        frame = pd.DataFrame(frame, columns=RISK_COLUMNS)
    risks = []
    for _, row in frame.iterrows():
        name = str(row.get("name", "")).strip()
        if not name or name.lower() == "nan":
            continue
        risks.append(RiskExposure(
            name=name,
            category=str(row.get("category", "Other")),
            annual_frequency=float(row.get("annual_frequency", 0) or 0),
            typical_loss=float(row.get("typical_loss", 0) or 0),
            large_loss=float(row.get("large_loss", 0) or 0),
            extreme_loss=float(row.get("extreme_loss", 0) or 0),
            severity_distribution=str(row.get("severity_distribution", "lognormal")),
            frequency_distribution=str(row.get("frequency_distribution", "poisson")),
            control_effectiveness=float(row.get("control_effectiveness_pct", 0) or 0) / 100,
            systemic_sensitivity=float(row.get("systemic_sensitivity", 0) or 0),
        ).validated())
    if not risks:
        raise ValueError("Add at least one valid risk exposure.")
    return risks


def money(x: float) -> str:
    if abs(x) >= 1_000_000_000:
        return f"$" + f"{x / 1_000_000_000:.2f}B"
    if abs(x) >= 1_000_000:
        return f"$" + f"{x / 1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"$" + f"{x / 1_000:.1f}K"
    return f"$" + f"{x:,.0f}"


def loss_figure(base, alternative=None):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=base.result.total_losses, nbinsx=65, histnorm="probability density", name="Current"))
    if alternative is not None:
        fig.add_trace(go.Histogram(x=alternative.result.total_losses, nbinsx=65, histnorm="probability density", name="Selected scenario", opacity=.55))
    for x, label in [(base.metrics.expected_loss, "Expected"), (base.metrics.reserve, "Reserve"), (base.metrics.var_95, "VaR95"), (base.metrics.var_99, "VaR99")]:
        fig.add_vline(x=x, line_dash="dash", annotation_text=label)
    fig.update_layout(title="Modeled annual loss distribution", barmode="overlay", xaxis_title="Annual loss", yaxis_title="Probability density")
    return fig


def exceedance_figure(base):
    curve = exceedance_curve(base.result.total_losses)
    fig = go.Figure(go.Scatter(x=curve["loss"], y=curve["exceedance"], mode="lines"))
    fig.update_layout(title="Loss exceedance curve", xaxis_title="Loss threshold", yaxis_title="Probability of exceedance", yaxis_tickformat=".0%")
    return fig


def contribution_figure(frame: pd.DataFrame):
    ordered = frame.sort_values("tail_contribution")
    fig = go.Figure()
    fig.add_bar(y=ordered["risk"], x=ordered["expected_contribution"], orientation="h", name="Expected loss")
    fig.add_bar(y=ordered["risk"], x=ordered["tail_contribution"], orientation="h", name="95% tail")
    fig.update_layout(title="Risk contribution", barmode="group", xaxis_tickformat=".0%")
    return fig


def driver_figure(frame: pd.DataFrame):
    return go.Figure(go.Scatter(
        x=frame["expected_loss"],
        y=frame["tail_contribution"],
        mode="markers+text",
        text=frame["risk"],
        textposition="top center",
    )).update_layout(title="Expected loss vs tail importance", xaxis_title="Expected loss", yaxis_title="Tail contribution", yaxis_tickformat=".0%")


def run_analysis_ui(
    scenario_name,
    annual_income_revenue,
    reserve,
    risk_tolerance,
    risk_table,
    simulations,
    seed,
    dependency_enabled,
    stress_preset,
    custom_frequency_shock,
    custom_severity_shock,
    control_degradation,
    selected_mitigations,
    custom_threshold,
    confidence_pct,
):
    risks = parse_risk_table(risk_table)
    n = int(simulations)
    seed = int(seed)
    base = analyze(risks, float(reserve), float(risk_tolerance), n, seed, bool(dependency_enabled))

    if stress_preset == "Custom":
        shocks = (float(custom_frequency_shock), float(custom_severity_shock), float(control_degradation))
    else:
        shocks = STRESS_PRESETS[str(stress_preset)]
    stressed = apply_global_stress(risks, *shocks)

    actions = SCENARIOS[str(scenario_name)].mitigations
    selected = set(selected_mitigations or [])
    alternative_risks, mitigation_cost = apply_mitigations(stressed, actions, selected)
    alternative = analyze(alternative_risks, float(reserve), float(risk_tolerance), n, seed, bool(dependency_enabled))

    threshold = float(custom_threshold)
    breach = float(np.mean(base.result.total_losses > threshold))
    confidence = float(confidence_pct) / 100
    conf_reserve = required_reserve(base.result.total_losses, confidence)

    kpis = (
        f"**Expected loss:** {money(base.metrics.expected_loss)}  |  "
        f"**VaR95:** {money(base.metrics.var_95)}  |  "
        f"**VaR99:** {money(base.metrics.var_99)}  |  "
        f"**ES95:** {money(base.metrics.es_95)}  |  "
        f"**Reserve breach:** {base.metrics.reserve_breach_probability:.1%}  |  "
        f"**Custom threshold breach:** {breach:.1%}  |  "
        f"**Reserve for {confidence:.1%}:** {money(conf_reserve)}"
    )

    contrib = base.contributions.copy()
    table = contrib.copy()
    table["expected_contribution"] *= 100
    table["tail_contribution"] *= 100

    comparison = pd.DataFrame([
        ["Expected loss", base.metrics.expected_loss, alternative.metrics.expected_loss],
        ["VaR 95", base.metrics.var_95, alternative.metrics.var_95],
        ["Expected Shortfall 95", base.metrics.es_95, alternative.metrics.es_95],
        ["Reserve breach probability", base.metrics.reserve_breach_probability, alternative.metrics.reserve_breach_probability],
        ["Annual mitigation cost", 0.0, mitigation_cost],
    ], columns=["Metric", "Current", "Selected scenario"])
    comparison["Change"] = comparison["Selected scenario"] - comparison["Current"]

    decision = decision_interpretation(base.metrics, contrib, float(annual_income_revenue))
    mitigation = (
        f"Selected scenario expected loss: **{money(alternative.metrics.expected_loss)}** versus "
        f"**{money(base.metrics.expected_loss)}** current. Annual selected mitigation cost: **{money(mitigation_cost)}**."
    )
    return kpis, loss_figure(base, alternative), exceedance_figure(base), contribution_figure(contrib), driver_figure(contrib), table, comparison, decision, mitigation


def load_scenario_ui(name):
    s = SCENARIOS[name]
    return s.annual_income_revenue, s.reserve, s.risk_tolerance, scenario_to_table(name), gr.update(choices=[m.name for m in s.mitigations], value=[]), s.reserve


def build_app() -> gr.Blocks:
    default = SCENARIOS[DEFAULT_SCENARIO]
    with gr.Blocks(title="Risk Exposure & Loss Distribution") as demo:
        gr.Markdown("# Risk Intelligence Lab\n## Risk Exposure & Loss Distribution Model\nInteractive quantitative risk management from individual/household scale to large organizations.")
        with gr.Row():
            with gr.Column(scale=1):
                scenario = gr.Dropdown(list(SCENARIOS), value=DEFAULT_SCENARIO, label="Preset scenario")
                scale = gr.Number(default.annual_income_revenue, label="Annual income / revenue")
                reserve = gr.Number(default.reserve, label="Available reserve")
                tolerance = gr.Number(default.risk_tolerance, label="Risk tolerance")
                simulations = gr.Slider(10_000, 250_000, 50_000, step=10_000, label="Monte Carlo runs")
                seed = gr.Number(42, label="Random seed")
                dependency = gr.Checkbox(True, label="Enable common-factor dependency")
                run = gr.Button("Run risk analysis", variant="primary")
            with gr.Column(scale=3):
                kpis = gr.Markdown("Run the model to populate metrics.")
                distribution = gr.Plot()

        with gr.Tab("Risk Builder"):
            risks = gr.Dataframe(scenario_to_table(DEFAULT_SCENARIO), headers=RISK_COLUMNS, interactive=True)
        with gr.Tab("Loss Analytics"):
            threshold = gr.Number(default.reserve, label="Custom loss threshold")
            confidence = gr.Slider(80, 99.9, 95, step=.1, label="Reserve confidence target %")
            exceedance = gr.Plot()
            contribution = gr.Plot()
            driver = gr.Plot()
            contribution_table = gr.Dataframe(interactive=False)
        with gr.Tab("Stress & Mitigation"):
            stress = gr.Dropdown(list(STRESS_PRESETS) + ["Custom"], value="Base", label="Stress scenario")
            freq = gr.Slider(-50, 150, 0, step=5, label="Custom frequency shock %")
            sev = gr.Slider(-50, 150, 0, step=5, label="Custom severity shock %")
            controls = gr.Slider(0, 100, 0, step=5, label="Control degradation %")
            mitigations = gr.CheckboxGroup([m.name for m in default.mitigations], label="Mitigation actions")
            comparison = gr.Dataframe(interactive=False)
            mitigation_text = gr.Markdown()
        with gr.Tab("Decision Summary"):
            decision = gr.Markdown()

        scenario.change(load_scenario_ui, scenario, [scale, reserve, tolerance, risks, mitigations, threshold])
        run.click(
            run_analysis_ui,
            [scenario, scale, reserve, tolerance, risks, simulations, seed, dependency, stress, freq, sev, controls, mitigations, threshold, confidence],
            [kpis, distribution, exceedance, contribution, driver, contribution_table, comparison, decision, mitigation_text],
        )
    return demo
