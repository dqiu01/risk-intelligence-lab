# risk-intelligence-lab

**Interactive quantitative risk intelligence for individuals, households, independent operators, and organizations of every size.**

This repository is a portfolio of working quantitative risk-management applications designed to scale with **exposure, complexity, and decision stakes rather than headcount or organizational form**. Each flagship model separates a reusable quantitative engine from a user-friendly interactive interface so the mathematics can be inspected, tested, and experienced rather than presented only as static formulas.

## Portfolio status

**8 / 8 flagship models implemented.**

| # | Model | Status | Quantitative capability |
|---:|---|---|---|
| 01 | [Risk Exposure & Loss Distribution](models/01-risk-exposure-loss-distribution/) | **Implemented** | Frequency/severity modeling, Monte Carlo aggregate loss, VaR/ES, tail attribution, reserve adequacy, mitigation |
| 02 | [Liquidity / Cash-Flow-at-Risk](models/02-liquidity-cashflow-risk/) | **Implemented** | Stochastic cash paths, liquidity-breach and insolvency probability, Cash-Flow-at-Risk, buffer sizing |
| 03 | [Market / Portfolio Risk](models/03-market-portfolio-risk/) | **Implemented** | Fat-tail correlated returns, VaR/ES, drawdown distributions, tail contribution, portfolio stress P&L |
| 04 | [Credit / Counterparty Risk](models/04-credit-counterparty-risk/) | **Implemented** | PD/LGD/EAD, correlated defaults, expected/unexpected loss, concentration, tail attribution, credit stress |
| 05 | [Monte Carlo Scenario Engine](models/05-monte-carlo-scenario-engine/) | **Implemented** | Continuous uncertainty propagation, dependency, target-miss probability, downside convexity, driver importance |
| 06 | [Stress & Reverse Stress Testing](models/06-stress-reverse-stress/) | **Implemented** | Nonlinear forward stress, breakpoints, constrained reverse-stress optimization, interaction losses |
| 07 | [Risk-Constrained Decision Optimization](models/07-risk-constrained-optimization/) | **Implemented** | Capital allocation under budget/cap/risk constraints, efficient frontier, correlated risk contribution |
| 08 | [Integrated Risk / Dependency Engine](models/08-integrated-risk-dependency/) | **Implemented** | Marginal loss distributions, copula-style dependency, diversification benefit, dependency stress, tail contribution |

## What the portfolio demonstrates

The models intentionally solve different risk problems rather than repeating the same Monte Carlo pattern under different names.

- **Measure loss:** quantify frequency, severity, expected loss, and tail loss.
- **Protect liquidity:** simulate cash paths and calculate breach, insolvency, and buffer requirements.
- **Measure market exposure:** model correlated fat-tail returns, drawdowns, and stressed portfolio losses.
- **Quantify counterparty risk:** combine PD, LGD, EAD, concentration, and correlated default behavior.
- **Propagate uncertainty:** translate uncertain continuous drivers into decision-outcome distributions.
- **Stress resilience:** test predefined shocks and solve backward for conditions that breach risk capacity.
- **Optimize decisions:** allocate scarce capital while explicitly constraining modeled risk.
- **Integrate dependencies:** show how diversification changes when separate risks share common drivers.

Together they demonstrate a complete quantitative risk workflow:

**identify uncertainty → quantify exposure → model dependency → simulate outcomes → inspect tails → stress assumptions → evaluate treatment → optimize decisions → communicate the result**

## Interactive-first design

Each model includes a **Gradio + Plotly** interface so a user can change assumptions and immediately see what those changes do to the modeled risk.

The surface is intentionally understandable to a non-quantitative user, while the underlying engine exposes distributions, simulations, optimization, attribution, stress logic, and validation for technical review.

## Scale

Synthetic presets deliberately span multiple levels:

**individual / household → solo professional → small business → mid-market organization → large organization**

The mathematics scales with the problem. The repository does not assume that meaningful risk management begins only when a company has a board, departments, or a large employee count.

## Quality controls

Every flagship model includes:

- reusable quantitative logic separated from the UI;
- an interactive application;
- synthetic cross-scale examples;
- automated tests;
- numerical or behavioral validation;
- a model card documenting assumptions and limitations;
- a README explaining method and interpretation;
- reproducible random seeds where simulation is used.

Local verification before the final repository integration produced **53 passing automated tests across the eight flagship modules**, and each interactive application was instantiated successfully. GitHub Actions runs the full eight-model matrix on pushes and pull requests.

## Repository structure

```text
risk-intelligence-lab/
├── README.md
├── BUILD_STATUS.md
├── .github/workflows/test.yml
└── models/
    ├── 01-risk-exposure-loss-distribution/
    ├── 02-liquidity-cashflow-risk/
    ├── 03-market-portfolio-risk/
    ├── 04-credit-counterparty-risk/
    ├── 05-monte-carlo-scenario-engine/
    ├── 06-stress-reverse-stress/
    ├── 07-risk-constrained-optimization/
    └── 08-integrated-risk-dependency/
```

## Important interpretation note

All built-in scenarios are **synthetic demonstrations**, not estimates for a specific real person, household, company, security, or industry. Model outputs are conditional on the entered assumptions. Each module documents its own limitations and should be calibrated and independently validated before any production use.
