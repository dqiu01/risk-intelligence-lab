# Stress & Reverse Stress Testing

> **Engine component:** This directory contains quantitative engine logic used by the single browser interface in `web/`. It is intentionally not a standalone application.

Forward stress asks **“what happens if these shocks occur?”** Reverse stress asks **“what is the smallest modeled combination of adverse conditions that reaches the loss capacity I care about?”**

## Quantitative design

Each factor has a maximum adverse move, a linear loss at that maximum, optional quadratic convexity, and a plausibility weight. A portfolio-level interaction term makes simultaneous shocks more damaging. Reverse stress uses constrained nonlinear optimization to minimize weighted shock distance subject to loss reaching the capacity boundary.

## Outputs

Forward scenario losses, capacity usage, optimized reverse-stress combination, actual adverse changes by factor, single-factor breakpoints, and a two-factor loss surface.

\`\`\`bash
# From the repository root
python -m http.server 8000
# Open http://localhost:8000/web/
\`\`\`

Synthetic presets only. Reverse-stress results are conditional on the configured loss functions; they are not forecasts.
