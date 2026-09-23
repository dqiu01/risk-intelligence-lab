# Monte Carlo Scenario Engine

> **Engine component:** This directory is part of the unified Risk Intelligence Lab. `panel.py` is an interface adapter and is not a standalone application. Launch the complete lab from the repository root with `python app.py`.

A general uncertainty-propagation engine that converts multiple correlated drivers into a distribution of decision outcomes. Unlike the event-loss model, this project models **continuous business/personal drivers** such as income, demand, pricing, costs, rates, and mix.

## Outputs

Expected/median/P05/P95 outcome, probability of missing a target, expected shortfall below target, Outcome-at-Risk 95, driver-importance analytics, and deterministic multi-sigma stress scenarios.

## Method

Each driver has a volatility, outcome impact per 1% move, and systemic loading. A shared factor creates dependence across drivers; idiosyncratic shocks preserve driver-specific uncertainty. Optional downside convexity makes combined adverse environments more damaging than a purely linear model.

```bash
cd ../..
pip install -r requirements.txt
python app.py
```

Presets are synthetic. Driver importance is statistical association, not causal proof.
