# Risk Exposure & Loss Distribution Model

> **Engine component:** This directory is part of the unified Risk Intelligence Lab. `panel.py` is an interface adapter and is not a standalone application. Launch the complete lab from the repository root with `python app.py`.

> Interactive quantitative risk-management showcase: turn uncertain event frequency and loss severity into aggregate loss distributions, tail-risk measures, reserve adequacy, stress tests, and mitigation decisions.

## Why this project exists

Traditional risk registers list risks as labels. This project demonstrates the next step: **quantifying what those risks can cost, how they combine, what the tail looks like, and how risk treatment changes the distribution**.

The interface is deliberately user-friendly. A user can start with a synthetic preset, edit risk assumptions, run Monte Carlo simulations, inspect expected and tail loss, stress the portfolio, select mitigations, and compare outcomes. The quantitative engine is isolated from the UI so the same model can be reused in notebooks, APIs, or another front end.

## What the model answers

- What is the modeled expected annual loss?
- How different is a typical year from a severe year?
- What are VaR 95, VaR 99, and Expected Shortfall?
- What is the modeled probability that losses exceed available reserves?
- How much reserve corresponds to a selected confidence level?
- Which risks dominate expected loss versus tail loss?
- How do stress conditions change the exposure?
- How much modeled risk reduction does a mitigation package buy?

## Interactive interface

The Gradio + Plotly application contains four working areas:

1. **Risk Builder** — edit event frequency, typical / large / extreme losses, distributions, existing controls, and systemic sensitivity.
2. **Loss Analytics** — inspect the aggregate loss distribution, exceedance curve, expected-loss contribution, 95% tail contribution, and expected-vs-tail driver matrix.
3. **Stress & Mitigation** — apply preset or custom shocks and select synthetic mitigation actions with explicit annual cost.
4. **Decision Summary** — translate model outputs into a concise decision-oriented interpretation while preserving clear model limitations.

### Run locally

```bash
# From the repository root
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

## Quantitative architecture

For each enabled risk, annual event frequency is sampled from a frequency model and event severities from a calibrated severity distribution. Aggregate annual loss is the sum of all simulated event losses across all modeled risk sources.

**Frequency models:** Poisson, Negative Binomial  
**Severity models:** Lognormal, Gamma, Triangular

User-friendly inputs are calibrated into distribution parameters. `typical_loss` acts as a central amount, `large_loss` as a high-but-plausible loss input, and `extreme_loss` as an explicit tail cap. Existing control effectiveness reduces residual severity. Mitigation actions can separately reduce frequency and severity.

A mean-one common lognormal factor can shift event frequencies for risks with positive `systemic_sensitivity`, introducing interpretable positive dependence without requiring the user to edit a full correlation matrix.

## Risk measures

The engine calculates:

- Expected and median loss
- Standard deviation
- VaR 95 and VaR 99
- Expected Shortfall 95 and 99
- Reserve exceedance probability
- Risk-tolerance exceedance probability
- Reserve required for a target confidence level
- Expected-loss contribution by risk
- Conditional tail-loss contribution by risk

Expected Shortfall is included deliberately: a percentile threshold alone does not describe how severe losses are after that threshold is crossed.

## Preset scenarios

All presets are **synthetic and illustrative**. They are not estimates for any real person, household, business, organization, or industry.

| Preset | Purpose |
|---|---|
| Individual / Household | Personal and household exposure, reserve adequacy, and mitigation trade-offs |
| Solo Professional | The same quantitative framework for a one-person operation |
| Growing Small Business | Default walkthrough for loss distribution, reserve adequacy, and mitigation |
| Growth SaaS Company | Concentration, churn, payment, and service-interruption exposures |
| Mid-Market Manufacturer | Demand, credit, production, input-price, and inventory risks |
| Diversified Enterprise | High-value multi-risk aggregation and systemic sensitivity |

## Example default output

With 100,000 simulations and seed 42, the synthetic **Growing Small Business** preset produces approximately:

| Metric | Modeled result |
|---|---:|
| Expected annual loss | $135K |
| Median annual loss | $109K |
| VaR 95 | $342K |
| VaR 99 | $484K |
| Expected Shortfall 95 | $430K |
| Reserve | $300K |
| Reserve breach probability | 8.0% |

These numbers can vary slightly with simulation count and random seed.

## Validation

The automated test suite checks deterministic reproducibility, analytical versus simulated expected loss, severity bounds, VaR/Expected Shortfall ordering, reserve quantiles, attribution reconciliation, dependency behavior, mitigation monotonicity, stress monotonicity, preset schema validation, and end-to-end UI analysis logic.

```bash
pytest
python validation/validate_model.py
```

See [validation/VALIDATION.md](validation/VALIDATION.md) and [validation/convergence.csv](validation/convergence.csv).

## Modeling limitations

This is a portfolio demonstration of quantitative risk techniques, not a production capital model.

- Preset inputs are synthetic rather than estimated from real loss data.
- Simple-mode calibration uses only a few user-friendly loss inputs.
- The dependence model is a common frequency factor, not a full copula or causal graph.
- Mitigation effectiveness is user-specified and is not inferred causally.
- Extreme-loss caps materially affect tail measures.
- Parameter and model uncertainty are not yet propagated separately.

## Planned extensions

- Empirical severity distributions
- Parameter uncertainty / Bayesian updating
- Richer dependence and copula models
- Reverse stress search
- Sensitivity tornado charts
- Mitigation optimization / efficient frontier
- Import of user-owned loss-event data

## Disclaimer

This repository is an educational and portfolio demonstration. Outputs are modeled estimates conditional on user-entered assumptions and are not forecasts, guarantees, financial advice, insurance advice, or substitutes for professional risk assessment.
