from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

FrequencyDistribution = Literal["poisson", "negative_binomial"]
SeverityDistribution = Literal["lognormal", "gamma", "triangular"]


@dataclass(frozen=True)
class RiskExposure:
    """User-friendly risk definition used by the simulation engine.

    `typical_loss` is interpreted as a median-like central loss amount.
    `large_loss` is interpreted as a high-but-plausible loss (approximately P90)
    for parametric calibration. `extreme_loss` is an upper truncation used to
    prevent unrealistic infinite-tail extrapolation in showcase scenarios.
    """

    name: str
    category: str
    annual_frequency: float
    typical_loss: float
    large_loss: float
    extreme_loss: float
    severity_distribution: SeverityDistribution = "lognormal"
    frequency_distribution: FrequencyDistribution = "poisson"
    control_effectiveness: float = 0.0
    systemic_sensitivity: float = 0.0
    nb_dispersion: float = 2.0
    enabled: bool = True

    def validated(self) -> "RiskExposure":
        if not self.name.strip():
            raise ValueError("Risk name cannot be empty.")
        if self.annual_frequency < 0:
            raise ValueError(f"{self.name}: annual_frequency must be >= 0.")
        if self.typical_loss < 0 or self.large_loss < 0 or self.extreme_loss < 0:
            raise ValueError(f"{self.name}: loss amounts must be non-negative.")
        if self.large_loss < self.typical_loss:
            raise ValueError(f"{self.name}: large_loss must be >= typical_loss.")
        if self.extreme_loss < self.large_loss:
            raise ValueError(f"{self.name}: extreme_loss must be >= large_loss.")
        if not 0 <= self.control_effectiveness < 1:
            raise ValueError(f"{self.name}: control_effectiveness must be in [0, 1).")
        if not 0 <= self.systemic_sensitivity <= 1:
            raise ValueError(f"{self.name}: systemic_sensitivity must be in [0, 1].")
        if self.nb_dispersion <= 0:
            raise ValueError(f"{self.name}: nb_dispersion must be > 0.")
        return self

    @property
    def residual_severity_multiplier(self) -> float:
        return 1.0 - self.control_effectiveness

    def with_stress(self, frequency_multiplier: float = 1.0, severity_multiplier: float = 1.0) -> "RiskExposure":
        if frequency_multiplier < 0 or severity_multiplier < 0:
            raise ValueError("Stress multipliers must be non-negative.")
        return replace(
            self,
            annual_frequency=self.annual_frequency * frequency_multiplier,
            typical_loss=self.typical_loss * severity_multiplier,
            large_loss=self.large_loss * severity_multiplier,
            extreme_loss=self.extreme_loss * severity_multiplier,
        )

    def with_mitigation(self, frequency_reduction: float = 0.0, severity_reduction: float = 0.0) -> "RiskExposure":
        if not 0 <= frequency_reduction <= 1:
            raise ValueError("frequency_reduction must be in [0, 1].")
        if not 0 <= severity_reduction <= 1:
            raise ValueError("severity_reduction must be in [0, 1].")
        return replace(
            self,
            annual_frequency=self.annual_frequency * (1.0 - frequency_reduction),
            typical_loss=self.typical_loss * (1.0 - severity_reduction),
            large_loss=self.large_loss * (1.0 - severity_reduction),
            extreme_loss=self.extreme_loss * (1.0 - severity_reduction),
        )


@dataclass(frozen=True)
class MitigationAction:
    name: str
    risk_name: str
    annual_cost: float
    frequency_reduction: float = 0.0
    severity_reduction: float = 0.0

    def validated(self) -> "MitigationAction":
        if self.annual_cost < 0:
            raise ValueError("annual_cost must be non-negative.")
        if not 0 <= self.frequency_reduction <= 1:
            raise ValueError("frequency_reduction must be in [0, 1].")
        if not 0 <= self.severity_reduction <= 1:
            raise ValueError("severity_reduction must be in [0, 1].")
        return self


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    annual_income_revenue: float
    reserve: float
    risk_tolerance: float
    risks: tuple[RiskExposure, ...]
    mitigations: tuple[MitigationAction, ...] = ()

    def validated(self) -> "ScenarioConfig":
        if self.annual_income_revenue <= 0:
            raise ValueError("annual_income_revenue must be > 0.")
        if self.reserve < 0 or self.risk_tolerance < 0:
            raise ValueError("reserve and risk_tolerance must be non-negative.")
        for risk in self.risks:
            risk.validated()
        for mitigation in self.mitigations:
            mitigation.validated()
        return self
