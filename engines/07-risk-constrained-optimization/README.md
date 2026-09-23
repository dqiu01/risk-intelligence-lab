# Risk-Constrained Decision Optimization

> **Engine component:** This directory is part of the unified Risk Intelligence Lab. `panel.py` is an interface adapter and is not a standalone application. Launch the complete lab from the repository root with `python app.py`.

A quantitative decision model for allocating limited capital across competing choices while keeping a portfolio-style risk measure inside a specified limit.

## What it demonstrates

- Constrained nonlinear optimization
- Budget and per-option capacity constraints
- Correlated risk aggregation
- Expected-benefit / risk efficient frontier
- Euler-style risk contribution
- Optional risk-aversion penalty

The same mathematics can represent household allocation choices, a solo operator's capital decisions, business projects, mitigation programs, or large capital portfolios.

```bash
cd ../..
pip install -r requirements.txt
python app.py
```

Synthetic expected-benefit and risk inputs are illustrative, not forecasts or recommendations.
