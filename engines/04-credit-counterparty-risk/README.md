# Credit / Counterparty Risk

> **Engine component:** This directory contains quantitative engine logic used by the single browser interface in `web/`. It is intentionally not a standalone application.

Interactive correlated-default portfolio model using **PD × LGD × EAD** economics plus Monte Carlo tail analysis. It scales from personal receivables and solo-professional invoices to large counterparty portfolios.

## Outputs

Analytical and simulated expected loss, unexpected loss, VaR 95/99, Expected Shortfall, reserve-breach probability, EAD concentration, effective counterparty count, name-level expected-loss contribution, conditional tail-loss contribution, and PD/LGD stress scenarios.

## Method

Defaults are generated from a latent Gaussian model containing global, sector, and idiosyncratic factors. LGD can be stochastic using a beta distribution around the configured mean.

\`\`\`bash
# From the repository root
python -m http.server 8000
# Open http://localhost:8000/web/
\`\`\`

All presets are synthetic. The model does not produce credit ratings or lending recommendations.
