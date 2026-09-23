# Validation — Credit / Counterparty Risk

Synthetic Small B2B Receivables preset; deterministic LGD for analytical EL comparison.

| Simulations | Simulated EL | Relative error vs analytical EL | VaR95 | ES95 |
|---:|---:|---:|---:|---:|
| 10,000 | $18,981 | 1.00% | $108,000 | $155,410 |
| 50,000 | $18,757 | -0.19% | $108,000 | $154,585 |
| 100,000 | $18,769 | -0.13% | $108,000 | $155,939 |

Automated checks cover reproducibility, analytical-vs-simulated EL, stress monotonicity, tail attribution reconciliation, and concentration metrics.
