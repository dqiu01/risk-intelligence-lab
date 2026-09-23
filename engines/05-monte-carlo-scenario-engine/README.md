# Monte Carlo Scenario Engine

> **Engine component:** This directory contains quantitative engine logic used by the single browser interface in `web/`. It is intentionally not a standalone application.

A general uncertainty-propagation engine that converts multiple correlated drivers into a distribution of decision outcomes. Unlike the event-loss model, this project models **continuous business/personal drivers** such as income, demand, pricing, costs, rates, and mix.

## Outputs

Expected/median/P05/P95 outcome, probability of missing a target, expected shortfall below target, Outcome-at-Risk 95, driver-importance analytics, and deterministic multi-sigma stress scenarios.

## Method

Each driver has a volatility, outcome impact per 1% move, and systemic loading. A shared factor creates dependence across drivers; idiosyncratic shocks preserve driver-specific uncertainty. Optional downside convexity makes combined adverse environments more damaging than a purely linear model.

\`\`\`bash
# From the repository root
python -m http.server 8000
# Open http://localhost:8000/web/
\`\`\`

Presets are synthetic. Driver importance is statistical association, not causal proof.
