# Model Validation Report

This report is generated from the synthetic **Growing Small Business** preset. It validates numerical behavior; it does not claim real-world calibration.

## High-precision simulation

- Simulations: 250,000
- Seed: 42
- Expected annual loss: $135,338
- VaR 95: $344,331
- VaR 99: $486,936
- Expected Shortfall 95: $432,449
- Reserve breach probability: 8.04%

## Checks

- Reproducibility is enforced by explicit random seeds.
- Severity draws are non-negative and capped at scenario-defined extreme loss levels.
- Expected Shortfall is checked to be no lower than the corresponding VaR.
- Risk contributions reconcile to 100% of expected and tail loss.
- Mitigation scenarios are tested for monotonic risk reduction under positive reductions.
- Stress scenarios are tested for increasing modeled loss when frequency/severity shocks are positive.

## Convergence table

| simulations | simulated expected loss | analytical mean reference | relative error | VaR 95 | ES 95 | reserve breach |
|---:|---:|---:|---:|---:|---:|---:|
| 10,000 | 135,405 | 135,203 | 0.15% | 345,026 | 433,786 | 8.15% |
| 50,000 | 135,107 | 135,203 | -0.07% | 342,759 | 430,321 | 8.03% |
| 100,000 | 134,921 | 135,203 | -0.21% | 341,853 | 429,521 | 7.98% |
| 250,000 | 135,338 | 135,203 | 0.10% | 344,331 | 432,449 | 8.04% |
