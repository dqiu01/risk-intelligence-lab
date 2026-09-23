from __future__ import annotations

import numpy as np

from .schemas import RiskExposure


def effective_frequency(risk: RiskExposure, systemic_factor: np.ndarray | None = None) -> np.ndarray | float:
    base = float(risk.annual_frequency)
    if systemic_factor is None or risk.systemic_sensitivity == 0:
        return base
    beta = float(risk.systemic_sensitivity)
    # Lognormal mean-one multiplier. Positive systemic shocks increase frequency
    # across sensitive risks and induce interpretable positive dependence.
    return base * np.exp(beta * systemic_factor - 0.5 * beta * beta)


def sample_frequency(
    rng: np.random.Generator,
    risk: RiskExposure,
    n_simulations: int,
    systemic_factor: np.ndarray | None = None,
) -> np.ndarray:
    if n_simulations <= 0:
        raise ValueError("n_simulations must be positive.")
    lam = effective_frequency(risk, systemic_factor)
    if risk.frequency_distribution == "poisson":
        return rng.poisson(lam=lam, size=n_simulations)

    if risk.frequency_distribution == "negative_binomial":
        # Parameterization with mean = mu and variance = mu + mu^2 / r.
        mu = np.asarray(lam, dtype=float)
        r = float(risk.nb_dispersion)
        p = r / (r + mu)
        return rng.negative_binomial(r, p, size=n_simulations)

    raise ValueError(f"Unsupported frequency distribution: {risk.frequency_distribution}")
