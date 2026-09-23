from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import optimize, stats

from .schemas import RiskExposure


@dataclass(frozen=True)
class SeverityParams:
    distribution: str
    params: dict[str, float]
    cap: float


def _safe_positive(value: float, floor: float = 1e-9) -> float:
    return max(float(value), floor)


def calibrate_lognormal(typical: float, large: float, extreme: float) -> SeverityParams:
    if typical == 0:
        return SeverityParams("degenerate", {"value": 0.0}, extreme)
    median = _safe_positive(typical)
    p90 = _safe_positive(max(large, median))
    z90 = stats.norm.ppf(0.90)
    sigma = max(math.log(p90 / median) / z90, 1e-6)
    mu = math.log(median)
    return SeverityParams("lognormal", {"mu": mu, "sigma": sigma}, max(extreme, large))


def calibrate_gamma(typical: float, large: float, extreme: float) -> SeverityParams:
    if typical == 0:
        return SeverityParams("degenerate", {"value": 0.0}, extreme)
    median = _safe_positive(typical)
    p90 = _safe_positive(max(large, median * 1.000001))
    ratio = p90 / median

    def objective(log_shape: float) -> float:
        shape = math.exp(log_shape)
        q50 = stats.gamma.ppf(0.50, a=shape)
        q90 = stats.gamma.ppf(0.90, a=shape)
        return q90 / q50 - ratio

    try:
        root = optimize.brentq(objective, math.log(0.05), math.log(1e4), maxiter=200)
        shape = math.exp(root)
    except ValueError:
        shape = 1e4
    scale = median / stats.gamma.ppf(0.50, a=shape)
    return SeverityParams("gamma", {"shape": shape, "scale": scale}, max(extreme, large))


def calibrate_triangular(typical: float, large: float, extreme: float) -> SeverityParams:
    upper = max(extreme, large, typical)
    if upper == 0:
        return SeverityParams("degenerate", {"value": 0.0}, 0.0)
    mode = min(max(typical, 0.0), upper)
    c = mode / upper if upper else 0.0
    return SeverityParams("triangular", {"left": 0.0, "mode": mode, "right": upper, "c": c}, upper)


def calibrate_severity(risk: RiskExposure) -> SeverityParams:
    risk.validated()
    if risk.severity_distribution == "lognormal":
        return calibrate_lognormal(risk.typical_loss, risk.large_loss, risk.extreme_loss)
    if risk.severity_distribution == "gamma":
        return calibrate_gamma(risk.typical_loss, risk.large_loss, risk.extreme_loss)
    if risk.severity_distribution == "triangular":
        return calibrate_triangular(risk.typical_loss, risk.large_loss, risk.extreme_loss)
    raise ValueError(f"Unsupported severity distribution: {risk.severity_distribution}")


def sample_severity(rng: np.random.Generator, risk: RiskExposure, size: int) -> np.ndarray:
    if size <= 0:
        return np.zeros(0, dtype=float)
    params = calibrate_severity(risk)
    if params.distribution == "degenerate":
        samples = np.full(size, params.params["value"], dtype=float)
    elif params.distribution == "lognormal":
        samples = rng.lognormal(params.params["mu"], params.params["sigma"], size=size)
    elif params.distribution == "gamma":
        samples = rng.gamma(params.params["shape"], params.params["scale"], size=size)
    elif params.distribution == "triangular":
        samples = rng.triangular(params.params["left"], params.params["mode"], params.params["right"], size=size)
    else:
        raise RuntimeError("Unknown calibrated severity distribution.")

    samples = np.minimum(samples, params.cap)
    return samples * risk.residual_severity_multiplier


def analytical_severity_mean(risk: RiskExposure) -> float:
    params = calibrate_severity(risk)
    if params.distribution == "degenerate":
        return params.params["value"] * risk.residual_severity_multiplier
    if params.distribution == "triangular":
        raw = (params.params["left"] + params.params["mode"] + params.params["right"]) / 3.0
        return raw * risk.residual_severity_multiplier

    if params.distribution == "lognormal":
        mu, sigma, cap = params.params["mu"], params.params["sigma"], params.cap
        dist = stats.lognorm(s=sigma, scale=math.exp(mu))
    else:
        shape, scale, cap = params.params["shape"], params.params["scale"], params.cap
        dist = stats.gamma(a=shape, scale=scale)

    truncated_first_moment = dist.expect(lambda x: x, lb=0, ub=cap)
    capped_mean = truncated_first_moment + cap * dist.sf(cap)
    return float(capped_mean) * risk.residual_severity_multiplier
