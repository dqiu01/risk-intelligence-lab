# Liquidity / Cash-Flow-at-Risk

> **Engine component:** This directory contains quantitative engine logic used by the single browser interface in `web/`. It is intentionally not a standalone application.

Interactive cash-path simulation for individuals, solo operators, and organizations. The model propagates uncertain monthly income, fixed costs, variable costs, debt service, and delayed collections into a distribution of future cash balances.

## Decision questions

- What is the probability cash falls below a required minimum?
- What is the probability of insolvency during the horizon?
- How much additional starting liquidity is needed for a chosen protection level?
- How do reserve additions, cost reductions, and faster collections compare?
- How sensitive is liquidity to income and cost shocks?

## Quantitative outputs

Expected/median/P05 ending cash, Cash-Flow-at-Risk 95, minimum-path cash, liquidity breach probability, insolvency probability, and a 95% additional-buffer estimate.

## Run

\`\`\`bash
# From the repository root
python -m http.server 8000
# Open http://localhost:8000/web/
\`\`\`

Presets are synthetic and illustrative. Outputs are conditional scenario estimates, not forecasts or financial advice.
