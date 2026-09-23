# Risk-Constrained Decision Optimization

> **Engine component:** This directory contains quantitative engine logic used by the single browser interface in `web/`. It is intentionally not a standalone application.

A quantitative decision model for allocating limited capital across competing choices while keeping a portfolio-style risk measure inside a specified limit.

## What it demonstrates

- Constrained nonlinear optimization
- Budget and per-option capacity constraints
- Correlated risk aggregation
- Expected-benefit / risk efficient frontier
- Euler-style risk contribution
- Optional risk-aversion penalty

The same mathematics can represent household allocation choices, a solo operator's capital decisions, business projects, mitigation programs, or large capital portfolios.

\`\`\`bash
# From the repository root
python -m http.server 8000
# Open http://localhost:8000/web/
\`\`\`

Synthetic expected-benefit and risk inputs are illustrative, not forecasts or recommendations.
