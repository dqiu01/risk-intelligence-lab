# Model Card — Liquidity / Cash-Flow-at-Risk

**Purpose:** quantify liquidity-path uncertainty and evaluate reserve adequacy and practical interventions.

**Core assumptions:** monthly income and fixed-cost shocks are lognormal; income and costs have a modest adverse correlation; variable cost scales with generated income; a configurable share of collections is delayed one month.

**Key model risks:** parameter misspecification, ignoring multi-month receivables aging, no financing-line behavior, and simplified cost/income dependence.

**Validation:** reproducibility, bounded probabilities, adverse-shock monotonicity, and reserve-action monotonicity are automated.
