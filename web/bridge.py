from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

import engine02
import engine03
import engine04
import engine05
import engine06
import engine07
import engine08
from risk_model import analyze as analyze01
from risk_model import apply_global_stress as apply_global_stress01
from risk_model import load_all_scenarios as load_all_scenarios01

SCENARIOS01 = load_all_scenarios01(Path("/home/pyodide/engine01/scenarios"))


def _hist(values, bins=44):
    values = np.asarray(values, dtype=float)
    counts, edges = np.histogram(values, bins=bins)
    counts = counts / max(counts.sum(), 1)
    x = ((edges[:-1] + edges[1:]) / 2).tolist()
    return {"x": x, "y": counts.tolist()}


def _metric(label, value, fmt="number"):
    return {"label": label, "value": float(value), "format": fmt}


def _chart(title, traces, x_label="", y_label=""):
    return {
        "title": title,
        "traces": traces,
        "x_label": x_label,
        "y_label": y_label,
    }


def _result(metrics, charts, summary, note="Synthetic scenario; outputs are conditional on the assumptions entered."):
    return json.dumps({"metrics": metrics, "charts": charts, "summary": summary, "note": note})


def presets(engine_id):
    if engine_id == "01":
        return list(SCENARIOS01)
    module = {
        "02": engine02,
        "03": engine03,
        "04": engine04,
        "05": engine05,
        "06": engine06,
        "07": engine07,
        "08": engine08,
    }[engine_id]
    return list(module.PRESETS)


def presets_json(engine_id):
    return json.dumps(presets(engine_id))


def defaults(engine_id, preset):
    if engine_id == "01":
        s = SCENARIOS01[preset]
        return {
            "reserve": s.reserve,
            "risk_tolerance": s.risk_tolerance,
            "frequency_shock_pct": 0,
            "severity_shock_pct": 0,
            "simulations": 15000,
        }
    if engine_id == "02":
        s = engine02.PRESETS[preset]
        return {
            "starting_cash": s.starting_cash,
            "minimum_cash": s.minimum_cash,
            "income_shock_pct": 0,
            "cost_shock_pct": 0,
            "simulations": 15000,
        }
    if engine_id == "03":
        s = engine03.PRESETS[preset]
        return {
            "portfolio_value": s.portfolio_value,
            "correlation": s.correlation,
            "horizon_days": s.horizon_days,
            "simulations": 12000,
        }
    if engine_id == "04":
        s = engine04.PRESETS[preset]
        return {
            "reserve": s.reserve,
            "pd_multiplier": 1.0,
            "lgd_add_pct": 0,
            "simulations": 15000,
        }
    if engine_id == "05":
        s = engine05.PRESETS[preset]
        return {
            "base_outcome": s.base_outcome,
            "target": s.target,
            "systemic_stress": 0,
            "simulations": 15000,
        }
    if engine_id == "06":
        s = engine06.PRESETS[preset]
        return {
            "risk_capacity": s.risk_capacity,
        }
    if engine_id == "07":
        s = engine07.PRESETS[preset]
        return {
            "budget": s.budget,
            "risk_limit": s.risk_limit,
            "risk_aversion": 0,
        }
    if engine_id == "08":
        s = engine08.PRESETS[preset]
        return {
            "reserve": s.reserve,
            "dependency_scale": 1.0,
            "simulations": 12000,
        }
    raise KeyError(engine_id)


def defaults_json(engine_id, preset):
    return json.dumps(defaults(engine_id, preset))


def run01(preset, c):
    s = SCENARIOS01[preset]
    risks = apply_global_stress01(
        s.risks,
        float(c.get("frequency_shock_pct", 0)),
        float(c.get("severity_shock_pct", 0)),
        0,
    )
    reserve = float(c.get("reserve", s.reserve))
    tolerance = float(c.get("risk_tolerance", s.risk_tolerance))
    n = int(c.get("simulations", 15000))
    a = analyze01(risks, reserve, tolerance, n, 42, True)
    m = a.metrics
    h = _hist(a.result.total_losses)
    contrib = a.contributions.sort_values("tail_contribution", ascending=False)
    metrics = [
        _metric("Expected annual loss", m.expected_loss, "currency"),
        _metric("VaR 95", m.var_95, "currency"),
        _metric("Expected Shortfall 95", m.es_95, "currency"),
        _metric("Reserve breach", m.reserve_breach_probability, "percent"),
    ]
    charts = [
        _chart(
            "Aggregate annual loss distribution",
            [{"type": "bar", "name": "Probability", "x": h["x"], "y": h["y"]}],
            "Annual loss",
            "Probability",
        ),
        _chart(
            "Expected vs tail contribution",
            [
                {"type": "bar", "name": "Expected", "x": contrib["risk"].tolist(), "y": contrib["expected_contribution"].tolist()},
                {"type": "bar", "name": "95% tail", "x": contrib["risk"].tolist(), "y": contrib["tail_contribution"].tolist()},
            ],
            "Risk source",
            "Contribution",
        ),
    ]
    summary = (
        f"Expected modeled annual loss is ${m.expected_loss:,.0f}. "
        f"The 95% loss threshold is ${m.var_95:,.0f}, while average loss beyond that threshold is ${m.es_95:,.0f}. "
        f"With a reserve of ${reserve:,.0f}, modeled breach probability is {m.reserve_breach_probability:.1%}."
    )
    return _result(metrics, charts, summary)


def run02(preset, c):
    s = engine02.PRESETS[preset]
    s = replace(
        s,
        starting_cash=float(c.get("starting_cash", s.starting_cash)),
        minimum_cash=float(c.get("minimum_cash", s.minimum_cash)),
    )
    n = int(c.get("simulations", 15000))
    r = engine02.simulate_liquidity(
        s,
        n,
        42,
        float(c.get("income_shock_pct", 0)),
        float(c.get("cost_shock_pct", 0)),
    )
    m = engine02.summarize(r, s)
    p = engine02.percentile_paths(r)
    h = _hist(r.ending_cash)
    metrics = [
        _metric("Expected ending cash", m["expected_ending_cash"], "currency"),
        _metric("Cash-Flow-at-Risk 95", m["cashflow_at_risk_95"], "currency"),
        _metric("Liquidity breach", m["liquidity_breach_probability"], "percent"),
        _metric("Insolvency probability", m["insolvency_probability"], "percent"),
    ]
    charts = [
        _chart(
            "Ending cash distribution",
            [{"type": "bar", "name": "Probability", "x": h["x"], "y": h["y"]}],
            "Ending cash",
            "Probability",
        ),
        _chart(
            "Cash-path percentile envelope",
            [
                {"type": "line", "name": "P90", "x": p["month"].tolist(), "y": p["p90"].tolist()},
                {"type": "line", "name": "Median", "x": p["month"].tolist(), "y": p["median"].tolist()},
                {"type": "line", "name": "P10", "x": p["month"].tolist(), "y": p["p10"].tolist()},
            ],
            "Month",
            "Cash",
        ),
    ]
    summary = (
        f"Modeled probability of falling below the minimum cash threshold is {m['liquidity_breach_probability']:.1%}. "
        f"The 95% additional starting buffer estimate is ${m['required_additional_buffer_95']:,.0f}."
    )
    return _result(metrics, charts, summary)


def run03(preset, c):
    s = engine03.PRESETS[preset]
    s = replace(
        s,
        portfolio_value=float(c.get("portfolio_value", s.portfolio_value)),
        correlation=float(c.get("correlation", s.correlation)),
        horizon_days=int(c.get("horizon_days", s.horizon_days)),
    )
    n = int(c.get("simulations", 12000))
    r = engine03.simulate_market(s, n, 42)
    m = engine03.summarize(r)
    contrib = engine03.tail_contributions(r)
    h = _hist(r.losses)
    metrics = [
        _metric("VaR 95", m["var_95"], "currency"),
        _metric("Expected Shortfall 95", m["es_95"], "currency"),
        _metric("VaR 99", m["var_99"], "currency"),
        _metric("P95 max drawdown", m["p95_max_drawdown"], "percent"),
    ]
    charts = [
        _chart(
            "Portfolio loss distribution",
            [{"type": "bar", "name": "Probability", "x": h["x"], "y": h["y"]}],
            "Loss",
            "Probability",
        ),
        _chart(
            "95% tail-loss contribution",
            [{"type": "bar", "name": "Tail contribution", "x": contrib["asset"].tolist(), "y": contrib["tail_contribution"].tolist()}],
            "Asset",
            "Contribution",
        ),
    ]
    summary = (
        f"Over {s.horizon_days} trading days, modeled VaR95 is ${m['var_95']:,.0f} and ES95 is ${m['es_95']:,.0f}. "
        f"The simulated 95th-percentile maximum drawdown is {m['p95_max_drawdown']:.1%}."
    )
    return _result(metrics, charts, summary, "Synthetic market model; not investment advice.")


def run04(preset, c):
    s = engine04.PRESETS[preset]
    reserve = float(c.get("reserve", s.reserve))
    n = int(c.get("simulations", 15000))
    pdm = float(c.get("pd_multiplier", 1))
    lgd_add = float(c.get("lgd_add_pct", 0)) / 100
    r = engine04.simulate_credit(s.counterparties, n, 42, pdm, lgd_add)
    m = engine04.summarize(r, s.counterparties, reserve)
    contrib = engine04.contributions(r, s.counterparties)
    h = _hist(r.total_losses)
    metrics = [
        _metric("Expected credit loss", m["simulated_el"], "currency"),
        _metric("Unexpected loss", m["unexpected_loss"], "currency"),
        _metric("VaR 95", m["var_95"], "currency"),
        _metric("Reserve breach", m["reserve_breach_probability"], "percent"),
    ]
    charts = [
        _chart(
            "Credit-loss distribution",
            [{"type": "bar", "name": "Probability", "x": h["x"], "y": h["y"]}],
            "Credit loss",
            "Probability",
        ),
        _chart(
            "Counterparty tail contribution",
            [{"type": "bar", "name": "Tail contribution", "x": contrib["counterparty"].tolist(), "y": contrib["tail_contribution"].tolist()}],
            "Counterparty",
            "Contribution",
        ),
    ]
    summary = (
        f"At a PD multiplier of {pdm:.1f}x, expected modeled credit loss is ${m['simulated_el']:,.0f}. "
        f"Reserve-breach probability is {m['reserve_breach_probability']:.1%}."
    )
    return _result(metrics, charts, summary, "Synthetic counterparty model; not a credit rating or lending recommendation.")


def run05(preset, c):
    m0 = engine05.PRESETS[preset]
    m = replace(
        m0,
        base_outcome=float(c.get("base_outcome", m0.base_outcome)),
        target=float(c.get("target", m0.target)),
    )
    n = int(c.get("simulations", 15000))
    r = engine05.simulate(m, n, 42, float(c.get("systemic_stress", 0)))
    s = engine05.summarize(r, m.target, m.base_outcome)
    imp = engine05.driver_importance(r)
    h = _hist(r.outcomes)
    metrics = [
        _metric("Expected outcome", s["expected_outcome"], "currency"),
        _metric("P05 outcome", s["p05_outcome"], "currency"),
        _metric("Target miss", s["target_miss_probability"], "percent"),
        _metric("Outcome-at-Risk 95", s["outcome_at_risk_95"], "currency"),
    ]
    charts = [
        _chart(
            "Outcome distribution",
            [{"type": "bar", "name": "Probability", "x": h["x"], "y": h["y"]}],
            "Outcome",
            "Probability",
        ),
        _chart(
            "Driver importance",
            [{"type": "bar", "name": "Absolute importance", "x": imp["driver"].tolist(), "y": imp["absolute_importance"].tolist()}],
            "Driver",
            "Absolute correlation",
        ),
    ]
    summary = (
        f"Modeled probability of missing the target of ${m.target:,.0f} is {s['target_miss_probability']:.1%}. "
        f"The 5th-percentile outcome is ${s['p05_outcome']:,.0f}."
    )
    return _result(metrics, charts, summary)


def run06(preset, c):
    m0 = engine06.PRESETS[preset]
    m = replace(m0, risk_capacity=float(c.get("risk_capacity", m0.risk_capacity)))
    scenarios = engine06.scenario_table(m)
    rev = engine06.reverse_stress(m)
    rt = engine06.reverse_stress_table(m)
    nearest = rev["distance"] if rev["success"] else np.nan
    metrics = [
        _metric("Risk capacity", m.risk_capacity, "currency"),
        _metric("Moderate stress loss", scenarios.loc[scenarios["scenario"] == "Moderate", "modeled_loss"].iloc[0], "currency"),
        _metric("Reverse-stress distance", 0 if np.isnan(nearest) else nearest, "number"),
        _metric("Boundary loss", rev["loss"], "currency"),
    ]
    charts = [
        _chart(
            "Forward stress scenarios",
            [{"type": "bar", "name": "Modeled loss", "x": scenarios["scenario"].tolist(), "y": scenarios["modeled_loss"].tolist()}],
            "Stress severity",
            "Modeled loss",
        ),
        _chart(
            "Nearest reverse-stress combination",
            [{"type": "bar", "name": "Normalized shock", "x": rt["factor"].tolist(), "y": rt["normalized_shock"].tolist()}],
            "Risk factor",
            "Fraction of maximum shock",
        ),
    ]
    if rev["success"]:
        summary = (
            f"The nearest modeled combination that reaches the ${m.risk_capacity:,.0f} risk-capacity boundary "
            f"has weighted stress distance {rev['distance']:.3f}."
        )
    else:
        summary = "The configured risk capacity is not breached even at all maximum modeled shocks."
    return _result(metrics, charts, summary)


def run07(preset, c):
    s0 = engine07.PRESETS[preset]
    s = replace(
        s0,
        budget=float(c.get("budget", s0.budget)),
        risk_limit=float(c.get("risk_limit", s0.risk_limit)),
    )
    r = engine07.optimize_allocation(s, s.risk_limit, float(c.get("risk_aversion", 0)))
    t = engine07.allocation_table(s, r)
    f = engine07.efficient_frontier(s, 18)
    metrics = [
        _metric("Capital allocated", r["spent"], "currency"),
        _metric("Expected modeled benefit", r["expected_benefit"], "currency"),
        _metric("Portfolio risk", r["risk"], "currency"),
        _metric("Risk-limit use", r["risk"] / s.risk_limit if s.risk_limit else 0, "percent"),
    ]
    charts = [
        _chart(
            "Optimized allocation",
            [{"type": "bar", "name": "Allocation", "x": t["option"].tolist(), "y": t["allocation"].tolist()}],
            "Decision option",
            "Allocation",
        ),
        _chart(
            "Risk / benefit frontier",
            [{"type": "line", "name": "Efficient frontier", "x": f["realized_risk"].tolist(), "y": f["expected_benefit"].tolist()}],
            "Modeled risk",
            "Expected benefit",
        ),
    ]
    summary = (
        f"The optimizer allocates ${r['spent']:,.0f} and produces a modeled risk measure of ${r['risk']:,.0f} "
        f"against a ${s.risk_limit:,.0f} risk limit."
    )
    return _result(metrics, charts, summary)


def run08(preset, c):
    s = engine08.PRESETS[preset]
    reserve = float(c.get("reserve", s.reserve))
    scale = float(c.get("dependency_scale", 1))
    n = int(c.get("simulations", 12000))
    r = engine08.simulate_integrated(s.risks, n, 42, scale)
    m = engine08.summarize(r, s.risks, reserve)
    contrib = engine08.tail_contributions(r)
    curve = engine08.dependency_comparison(replace(s, reserve=reserve), min(n, 6000), 42)
    h = _hist(r.total_losses)
    metrics = [
        _metric("Expected integrated loss", m["expected_loss"], "currency"),
        _metric("VaR 95", m["var_95"], "currency"),
        _metric("Expected Shortfall 95", m["es_95"], "currency"),
        _metric("Diversification benefit", m["diversification_benefit_var95"], "currency"),
    ]
    charts = [
        _chart(
            "Integrated loss distribution",
            [{"type": "bar", "name": "Probability", "x": h["x"], "y": h["y"]}],
            "Total loss",
            "Probability",
        ),
        _chart(
            "Dependency stress curve",
            [
                {"type": "line", "name": "VaR95", "x": curve["correlation_scale"].tolist(), "y": curve["var_95"].tolist()},
                {"type": "line", "name": "ES95", "x": curve["correlation_scale"].tolist(), "y": curve["es_95"].tolist()},
            ],
            "Dependency scale",
            "Loss",
        ),
    ]
    summary = (
        f"At dependency scale {scale:.2f}, modeled VaR95 is ${m['var_95']:,.0f}. "
        f"The gap between summed stand-alone VaR and integrated VaR is ${m['diversification_benefit_var95']:,.0f}."
    )
    return _result(metrics, charts, summary)


RUNNERS = {
    "01": run01,
    "02": run02,
    "03": run03,
    "04": run04,
    "05": run05,
    "06": run06,
    "07": run07,
    "08": run08,
}


def run_json(engine_id, preset, config_json):
    config = json.loads(config_json)
    return RUNNERS[engine_id](preset, config)
