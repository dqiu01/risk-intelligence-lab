from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .metrics import LossMetrics, risk_contributions, summarize_losses
from .schemas import RiskExposure
from .simulation import SimulationResult, simulate_portfolio


@dataclass(frozen=True)
class ScenarioAnalysis:
    result: SimulationResult
    metrics: LossMetrics
    contributions: pd.DataFrame


def analyze(
    risks: list[RiskExposure] | tuple[RiskExposure, ...],
    reserve: float,
    risk_tolerance: float,
    n_simulations: int = 50_000,
    seed: int = 42,
    dependency_enabled: bool = True,
) -> ScenarioAnalysis:
    result = simulate_portfolio(risks, n_simulations, seed, dependency_enabled)
    metrics = summarize_losses(result, reserve, risk_tolerance)
    contributions = risk_contributions(result)
    return ScenarioAnalysis(result, metrics, contributions)


def compare_metrics(base: LossMetrics, alternative: LossMetrics, annual_cost: float = 0.0) -> pd.DataFrame:
    rows = [
        ("Expected loss", base.expected_loss, alternative.expected_loss),
        ("VaR 95", base.var_95, alternative.var_95),
        ("VaR 99", base.var_99, alternative.var_99),
        ("Expected shortfall 95", base.es_95, alternative.es_95),
        ("Reserve breach probability", base.reserve_breach_probability, alternative.reserve_breach_probability),
    ]
    frame = pd.DataFrame(rows, columns=["metric", "base", "alternative"])
    frame["change"] = frame["alternative"] - frame["base"]
    frame["annual_mitigation_cost"] = annual_cost
    return frame


def decision_interpretation(metrics: LossMetrics, contributions: pd.DataFrame, annual_income_revenue: float) -> str:
    top = contributions.iloc[0] if not contributions.empty else None
    reserve_status = "above" if metrics.var_95 > metrics.reserve else "within"
    expected_pct = 100 * metrics.expected_loss / annual_income_revenue if annual_income_revenue else 0.0
    top_text = (
        f"The largest modeled contributor to 95% tail losses is **{top['risk']}** "
        f"at approximately **{top['tail_contribution']:.1%}** of conditional tail loss."
        if top is not None else "No risk contribution data is available."
    )
    return (
        f"Based on the entered assumptions, modeled expected annual loss is **${metrics.expected_loss:,.0f}** "
        f"({expected_pct:.1f}% of annual income / revenue). The 95% loss level is **${metrics.var_95:,.0f}**, "
        f"which is {reserve_status} the current reserve of **${metrics.reserve:,.0f}**. "
        f"The modeled probability of losses exceeding that reserve is **{metrics.reserve_breach_probability:.1%}**. "
        f"{top_text} These figures are scenario-model outputs, not forecasts or guarantees."
    )
