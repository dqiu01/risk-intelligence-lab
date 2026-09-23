# risk-intelligence-lab

**Quantitative models, analytics, and decision frameworks for risk management across individuals, independent operators, and organizations of every size.**

This repository is a portfolio of interactive quantitative risk-management models designed to scale with **exposure, complexity, and decision stakes rather than headcount or organizational form**. An individual, household, solo operator, small business, mid-sized firm, and large organization can all face uncertainty that should be made measurable, stressable, and decision-relevant.

## Flagship models

| # | Model | Status | Core question |
|---:|---|---|---|
| 01 | [Risk Exposure & Loss Distribution](models/01-risk-exposure-loss-distribution/) | **Implemented** | How much can uncertain risk events cost, what does the tail look like, and how does mitigation change it? |
| 02 | Liquidity / Cash-Flow-at-Risk | Planned | What is the probability of breaching minimum liquidity or exhausting runway? |
| 03 | Market / Portfolio Risk | Planned | How large can market-driven losses become under normal and stressed conditions? |
| 04 | Credit / Counterparty Risk | Planned | How do PD, LGD, EAD, and concentration combine into loss exposure? |
| 05 | Monte Carlo Scenario Engine | Planned | What range of outcomes emerges when multiple uncertain drivers move together? |
| 06 | Stress & Reverse Stress Testing | Planned | Which conditions push the person, operation, or organization beyond its risk capacity? |
| 07 | Risk-Constrained Decision Optimization | Planned | How should scarce capital or mitigation budget be allocated under risk constraints? |
| 08 | Integrated Risk / Dependency Engine | Planned | How do interacting risks combine into total exposure across multiple risk sources? |

## Design standard

Each implemented model is intended to include:

- a working interactive interface;
- a reusable quantitative engine separate from the UI;
- synthetic preset scenarios from individual/household to large-organization scale;
- transparent assumptions and mathematical methodology;
- tail-risk and stress analysis where relevant;
- mitigation / decision comparisons;
- automated tests and numerical validation;
- explicit limitations and model-risk discussion.

The goal is not to collect notebooks. It is to demonstrate a complete workflow:

**identify uncertainty → quantify exposure → simulate outcomes → inspect tails → stress assumptions → evaluate treatment → support a decision**.
