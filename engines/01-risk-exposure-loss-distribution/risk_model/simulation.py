from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .frequency import sample_frequency
from .schemas import RiskExposure
from .severity import sample_severity


@dataclass(frozen=True)
class SimulationResult:
    total_losses: np.ndarray
    risk_losses: pd.DataFrame
    event_counts: pd.DataFrame
    seed: int

    @property
    def n_simulations(self) -> int:
        return len(self.total_losses)


def _aggregate_event_severities(
    rng: np.random.Generator,
    risk: RiskExposure,
    counts: np.ndarray,
) -> np.ndarray:
    n = counts.size
    totals = np.zeros(n, dtype=float)
    max_count = int(counts.max(initial=0))
    # Vectorized by event ordinal: efficient for general risk-event frequencies while
    # retaining event-level severity sampling and exact zero-event handling.
    for event_ordinal in range(max_count):
        active = counts > event_ordinal
        active_n = int(active.sum())
        if active_n:
            totals[active] += sample_severity(rng, risk, active_n)
    return totals


def simulate_portfolio(
    risks: list[RiskExposure] | tuple[RiskExposure, ...],
    n_simulations: int = 50_000,
    seed: int = 42,
    dependency_enabled: bool = True,
) -> SimulationResult:
    if n_simulations <= 0:
        raise ValueError("n_simulations must be positive.")
    enabled = [risk.validated() for risk in risks if risk.enabled]
    if not enabled:
        raise ValueError("At least one enabled risk is required.")

    rng = np.random.default_rng(seed)
    systemic = rng.standard_normal(n_simulations) if dependency_enabled else None

    loss_columns: dict[str, np.ndarray] = {}
    count_columns: dict[str, np.ndarray] = {}

    for risk in enabled:
        counts = sample_frequency(rng, risk, n_simulations, systemic)
        losses = _aggregate_event_severities(rng, risk, counts)
        loss_columns[risk.name] = losses
        count_columns[risk.name] = counts

    risk_losses = pd.DataFrame(loss_columns)
    event_counts = pd.DataFrame(count_columns)
    total_losses = risk_losses.sum(axis=1).to_numpy(dtype=float)
    return SimulationResult(total_losses, risk_losses, event_counts, seed)
