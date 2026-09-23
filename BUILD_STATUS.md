# Build Status

## risk-intelligence-lab flagship portfolio

**Portfolio implementation status: 8 / 8 models complete and published to `main`.**

| # | Model | Engine | Interactive UI | Tests | Validation | Model card |
|---:|---|:---:|:---:|:---:|:---:|:---:|
| 01 | Risk Exposure & Loss Distribution | ✅ | ✅ | ✅ | ✅ | ✅ |
| 02 | Liquidity / Cash-Flow-at-Risk | ✅ | ✅ | ✅ | ✅ | ✅ |
| 03 | Market / Portfolio Risk | ✅ | ✅ | ✅ | ✅ | ✅ |
| 04 | Credit / Counterparty Risk | ✅ | ✅ | ✅ | ✅ | ✅ |
| 05 | Monte Carlo Scenario Engine | ✅ | ✅ | ✅ | ✅ | ✅ |
| 06 | Stress & Reverse Stress Testing | ✅ | ✅ | ✅ | ✅ | ✅ |
| 07 | Risk-Constrained Decision Optimization | ✅ | ✅ | ✅ | ✅ | ✅ |
| 08 | Integrated Risk / Dependency Engine | ✅ | ✅ | ✅ | ✅ | ✅ |

## Verification completed before final integration

- **53 automated tests passed** across the eight flagship modules.
- Every Gradio application object instantiated successfully.
- Every validation runner completed and generated a validation report.
- Model 01's previously published GitHub CI run completed successfully.
- The repository CI workflow has now been expanded to test, build, and validate **all eight models independently** through a GitHub Actions matrix.

## Quantitative coverage

The completed portfolio demonstrates:

- frequency / severity loss modeling;
- aggregate Monte Carlo loss simulation;
- VaR and Expected Shortfall;
- cash-path and liquidity risk;
- fat-tail market and drawdown risk;
- PD / LGD / EAD credit risk;
- correlated defaults and concentration;
- continuous-driver scenario simulation;
- nonlinear stress and reverse-stress optimization;
- risk-constrained capital allocation;
- efficient-frontier analysis;
- risk contribution and tail attribution;
- copula-style dependency aggregation;
- diversification and dependency stress.

## Scope

The project is intentionally size-agnostic. Presets and interfaces range from **individuals and households to solo operators, small businesses, mid-market organizations, and large organizations**. Models scale by exposure and complexity rather than headcount.

## Authoritative GitHub repository

`dqiu01/risk-intelligence-lab`
