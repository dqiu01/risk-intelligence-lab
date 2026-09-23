# Build Status

## Model 01 — Risk Exposure & Loss Distribution

**Status: published to GitHub**

### Implemented

- Interactive Gradio + Plotly application
- Editable risk builder
- Synthetic presets from individual/household to diversified enterprise
- Poisson and Negative Binomial event-frequency models
- Lognormal, Gamma, and Triangular event-severity models
- Monte Carlo aggregate-loss simulation
- Mean-one common-factor dependency model
- Expected loss, median, volatility, VaR 95/99, Expected Shortfall 95/99
- Reserve/tolerance exceedance probabilities
- Confidence-based reserve calculation
- Expected-loss and 95% tail attribution
- Stress presets and custom stress controls
- Mitigation actions with explicit annual cost and frequency/severity effects
- Current-vs-selected-scenario comparison
- Decision-oriented interpretation
- Model card and explicit limitations
- Automated CI workflow
- Validation report and convergence data

### Verification

- 19 automated tests passed on the validated local build before publication.
- App object builds successfully.
- Local Gradio server returned HTTP 200.
- High-precision validation used 250,000 Monte Carlo runs with fixed seed 42.
- Default synthetic small-business scenario converged to approximately $135K expected annual loss and about 8% reserve-breach probability with a $300K reserve.

### GitHub target

Authoritative repository: `dqiu01/risk-intelligence-lab`.
