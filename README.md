# risk-intelligence-lab

**One interactive quantitative risk laboratory powered by eight risk engines.**

This repository is not a collection of eight standalone applications. It is a **single Risk Intelligence Lab interface** that lets a user experiment with different risk questions while the appropriate quantitative engine runs underneath.

The architecture is:

```text
                         ┌──────────────────────────────┐
                         │     Risk Intelligence Lab    │
                         │      unified interface       │
                         └──────────────┬───────────────┘
                                        │
          ┌───────────────┬─────────────┼─────────────┬───────────────┐
          │               │             │             │               │
   Loss Distribution   Liquidity     Market Risk   Credit Risk   Scenario Engine
          │               │             │             │               │
          └───────────────┴───────┬─────┴─────────────┴───────────────┘
                                  │
                     Stress / Optimization / Integrated Risk
```

Users remain inside the same application and switch between engine views. Each engine exposes editable assumptions, calculated risk metrics, and visual representations that make the underlying risk-management logic explorable.

## Run the lab

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

There is intentionally **one launch point: `app.py`**.

## Eight quantitative engines

| # | Engine | What the user can explore |
|---:|---|---|
| 01 | [Risk Exposure & Loss Distribution](engines/01-risk-exposure-loss-distribution/) | Event frequency/severity, Monte Carlo aggregate loss, VaR/ES, reserve adequacy, mitigation |
| 02 | [Liquidity / Cash-Flow-at-Risk](engines/02-liquidity-cashflow-risk/) | Cash paths, liquidity breach, insolvency, buffer sizing, action comparison |
| 03 | [Market / Portfolio Risk](engines/03-market-portfolio-risk/) | Fat-tail returns, VaR/ES, drawdowns, tail attribution, market stress |
| 04 | [Credit / Counterparty Risk](engines/04-credit-counterparty-risk/) | PD/LGD/EAD, correlated default, concentration, tail loss, credit stress |
| 05 | [Monte Carlo Scenario Engine](engines/05-monte-carlo-scenario-engine/) | Continuous uncertain drivers, dependency, target-miss probability, sensitivity |
| 06 | [Stress & Reverse Stress](engines/06-stress-reverse-stress/) | Forward shocks, breakpoints, nonlinear interaction, reverse-stress optimization |
| 07 | [Risk-Constrained Optimization](engines/07-risk-constrained-optimization/) | Capital allocation under budget/cap/risk constraints, efficient frontier |
| 08 | [Integrated Risk / Dependency](engines/08-integrated-risk-dependency/) | Cross-risk aggregation, diversification, common-factor dependency, tail contribution |

## Repository architecture

```text
risk-intelligence-lab/
├── app.py                     # the only runnable user interface
├── requirements.txt           # unified application dependencies
├── tests/                     # integrated interface tests
├── .github/workflows/test.yml
└── engines/
    ├── 01-risk-exposure-loss-distribution/
    │   ├── panel.py           # interface adapter, not a standalone app
    │   ├── risk_model/        # quantitative engine
    │   ├── tests/
    │   └── validation/
    ├── 02-liquidity-cashflow-risk/
    │   ├── panel.py
    │   ├── engine.py
    │   ├── tests/
    │   └── validation/
    └── ... through engine 08
```

### Separation of responsibilities

**The root interface**
- provides one consistent place to explore risk;
- routes the user to the selected engine;
- hosts the visual experiment environment.

**Engine panels**
- translate user controls into engine inputs;
- convert engine results into interactive visualizations;
- do not launch independently.

**Quantitative engines**
- contain the calculations, simulations, optimization, attribution, and stress logic;
- remain independently testable and reusable;
- do not own the application experience.

## Scale

The lab is designed for:

**individual / household → solo professional → small business → mid-market organization → large organization**

Risk-management sophistication scales with exposure and complexity rather than headcount.

## Quality controls

The CI pipeline now checks the architecture in two layers:

1. **Eight engine jobs** — unit tests and quantitative validation for every engine.
2. **One integrated-interface job** — verifies the single Risk Intelligence Lab application builds with all eight engines connected.

All included scenarios are synthetic demonstrations. Outputs are conditional on assumptions and are not forecasts or professional advice.
