from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .simulation import SimulationResult


@dataclass(frozen=True)
class LossMetrics:
    expected_loss: float
    median_loss: float
    standard_deviation: float
    var_95: float
    var_99: float
    es_95: float
    es_99: float
    reserve_breach_probability: float
    tolerance_breach_probability: float
    reserve: float
    risk_tolerance: float


def value_at_risk(losses: np.ndarray, confidence: float) -> float:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1).")
    return float(np.quantile(np.asarray(losses, dtype=float), confidence))


def expected_shortfall(losses: np.ndarray, confidence: float) -> float:
    arr = np.asarray(losses, dtype=float)
    var = value_at_risk(arr, confidence)
    tail = arr[arr >= var]
    return float(tail.mean()) if tail.size else var


def exceedance_probability(losses: np.ndarray, threshold: float) -> float:
    arr = np.asarray(losses, dtype=float)
    if arr.size == 0:
        raise ValueError("losses cannot be empty.")
    return float(np.mean(arr > threshold))


def required_reserve(losses: np.ndarray, confidence: float) -> float:
    return value_at_risk(losses, confidence)


def summarize_losses(result: SimulationResult, reserve: float, risk_tolerance: float) -> LossMetrics:
    losses = result.total_losses
    return LossMetrics(
        expected_loss=float(np.mean(losses)),
        median_loss=float(np.median(losses)),
        standard_deviation=float(np.std(losses, ddof=1)),
        var_95=value_at_risk(losses, 0.95),
        var_99=value_at_risk(losses, 0.99),
        es_95=expected_shortfall(losses, 0.95),
        es_99=expected_shortfall(losses, 0.99),
        reserve_breach_probability=exceedance_probability(losses, reserve),
        tolerance_breach_probability=exceedance_probability(losses, risk_tolerance),
        reserve=float(reserve),
        risk_tolerance=float(risk_tolerance),
    )


def risk_contributions(result: SimulationResult, confidence: float = 0.95) -> pd.DataFrame:
    expected_by_risk = result.risk_losses.mean(axis=0)
    expected_total = expected_by_risk.sum()

    var = value_at_risk(result.total_losses, confidence)
    tail_mask = result.total_losses >= var
    tail_by_risk = result.risk_losses.loc[tail_mask].mean(axis=0)
    tail_total = tail_by_risk.sum()

    frame = pd.DataFrame({
        "risk": expected_by_risk.index,
        "expected_loss": expected_by_risk.values,
        "expected_contribution": (expected_by_risk / expected_total).values if expected_total else 0.0,
        "tail_loss": tail_by_risk.reindex(expected_by_risk.index).values,
        "tail_contribution": (tail_by_risk / tail_total).reindex(expected_by_risk.index).values if tail_total else 0.0,
    })
    return frame.sort_values("tail_contribution", ascending=False).reset_index(drop=True)


def exceedance_curve(losses: np.ndarray, points: int = 200) -> pd.DataFrame:
    arr = np.sort(np.asarray(losses, dtype=float))
    if arr.size == 0:
        raise ValueError("losses cannot be empty.")
    probs = np.linspace(0.01, 0.999, points)
    amounts = np.quantile(arr, probs)
    return pd.DataFrame({"loss": amounts, "cdf": probs, "exceedance": 1.0 - probs})
