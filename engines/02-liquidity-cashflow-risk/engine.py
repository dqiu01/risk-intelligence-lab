from __future__ import annotations

from dataclasses import dataclass, replace
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LiquidityScenario:
    name: str
    starting_cash: float
    monthly_income: float
    fixed_cost: float
    variable_cost_pct: float
    debt_service: float
    minimum_cash: float
    income_volatility: float
    cost_volatility: float
    collection_delay_pct: float
    horizon_months: int = 12

    def validated(self) -> "LiquidityScenario":
        positive = [self.starting_cash, self.monthly_income, self.fixed_cost, self.debt_service, self.minimum_cash]
        if any(x < 0 for x in positive):
            raise ValueError("Cash, income, costs, debt service, and minimum cash must be non-negative.")
        if not 0 <= self.variable_cost_pct <= 1:
            raise ValueError("variable_cost_pct must be in [0, 1].")
        if not 0 <= self.collection_delay_pct <= 1:
            raise ValueError("collection_delay_pct must be in [0, 1].")
        if self.income_volatility < 0 or self.cost_volatility < 0:
            raise ValueError("Volatility must be non-negative.")
        if self.horizon_months < 1:
            raise ValueError("horizon_months must be positive.")
        return self


@dataclass(frozen=True)
class LiquidityResult:
    cash_paths: np.ndarray
    generated_income: np.ndarray
    cash_receipts: np.ndarray
    total_costs: np.ndarray

    @property
    def ending_cash(self) -> np.ndarray:
        return self.cash_paths[:, -1]

    @property
    def minimum_path_cash(self) -> np.ndarray:
        return self.cash_paths.min(axis=1)


PRESETS = {
    "Individual / Household": LiquidityScenario("Individual / Household", 30000, 10000, 5500, 0.08, 1200, 15000, 0.18, 0.08, 0.05),
    "Solo Professional": LiquidityScenario("Solo Professional", 45000, 15000, 6500, 0.18, 1000, 20000, 0.28, 0.10, 0.18),
    "Growing Small Business": LiquidityScenario("Growing Small Business", 300000, 440000, 190000, 0.36, 45000, 150000, 0.22, 0.09, 0.24),
    "Mid-Market Company": LiquidityScenario("Mid-Market Company", 9000000, 12500000, 4800000, 0.43, 700000, 4500000, 0.16, 0.07, 0.28),
    "Large Organization": LiquidityScenario("Large Organization", 240000000, 420000000, 155000000, 0.46, 22000000, 120000000, 0.13, 0.06, 0.30),
}


def simulate_liquidity(
    scenario: LiquidityScenario,
    n_simulations: int = 50000,
    seed: int = 42,
    income_shock_pct: float = 0.0,
    cost_shock_pct: float = 0.0,
    reserve_addition: float = 0.0,
    fixed_cost_reduction_pct: float = 0.0,
    collection_delay_reduction_pct: float = 0.0,
) -> LiquidityResult:
    s = scenario.validated()
    if n_simulations <= 0:
        raise ValueError("n_simulations must be positive.")
    rng = np.random.default_rng(seed)
    months = s.horizon_months

    rho = -0.25
    z1 = rng.standard_normal((n_simulations, months))
    z2 = rho * z1 + np.sqrt(1 - rho**2) * rng.standard_normal((n_simulations, months))

    income_base = s.monthly_income * (1 + income_shock_pct / 100)
    income = income_base * np.exp(s.income_volatility * z1 - 0.5 * s.income_volatility**2)

    fixed_base = s.fixed_cost * (1 + cost_shock_pct / 100) * (1 - fixed_cost_reduction_pct / 100)
    fixed = fixed_base * np.exp(s.cost_volatility * z2 - 0.5 * s.cost_volatility**2)
    variable = s.variable_cost_pct * income
    total_costs = fixed + variable + s.debt_service

    delay = np.clip(s.collection_delay_pct * (1 - collection_delay_reduction_pct / 100), 0, 1)
    prior = np.column_stack([np.full(n_simulations, income_base), income[:, :-1]])
    receipts = (1 - delay) * income + delay * prior

    cash = np.empty((n_simulations, months), dtype=float)
    balance = np.full(n_simulations, s.starting_cash + reserve_addition, dtype=float)
    for m in range(months):
        balance = balance + receipts[:, m] - total_costs[:, m]
        cash[:, m] = balance
    return LiquidityResult(cash, income, receipts, total_costs)


def summarize(result: LiquidityResult, scenario: LiquidityScenario) -> dict[str, float]:
    end = result.ending_cash
    min_cash = result.minimum_path_cash
    breach = min_cash < scenario.minimum_cash
    insolvent = min_cash < 0
    p05_end = float(np.quantile(end, 0.05))
    required_additional = np.maximum(scenario.minimum_cash - min_cash, 0)
    return {
        "expected_ending_cash": float(end.mean()),
        "median_ending_cash": float(np.median(end)),
        "p05_ending_cash": p05_end,
        "cashflow_at_risk_95": float(end.mean() - p05_end),
        "minimum_cash_p05": float(np.quantile(min_cash, 0.05)),
        "liquidity_breach_probability": float(breach.mean()),
        "insolvency_probability": float(insolvent.mean()),
        "required_additional_buffer_95": float(np.quantile(required_additional, 0.95)),
    }


def percentile_paths(result: LiquidityResult) -> pd.DataFrame:
    x = np.arange(1, result.cash_paths.shape[1] + 1)
    return pd.DataFrame({
        "month": x,
        "p10": np.quantile(result.cash_paths, 0.10, axis=0),
        "median": np.quantile(result.cash_paths, 0.50, axis=0),
        "p90": np.quantile(result.cash_paths, 0.90, axis=0),
    })


def compare_actions(scenario: LiquidityScenario, n: int = 30000, seed: int = 42) -> pd.DataFrame:
    actions = {
        "Current": {},
        "Add 25% reserve": {"reserve_addition": 0.25 * scenario.starting_cash},
        "Reduce fixed cost 10%": {"fixed_cost_reduction_pct": 10},
        "Improve collections 40%": {"collection_delay_reduction_pct": 40},
        "Combined": {"reserve_addition": 0.15 * scenario.starting_cash, "fixed_cost_reduction_pct": 7, "collection_delay_reduction_pct": 30},
    }
    rows = []
    for name, kwargs in actions.items():
        m = summarize(simulate_liquidity(scenario, n, seed, **kwargs), scenario)
        rows.append({"action": name, **m})
    return pd.DataFrame(rows)
