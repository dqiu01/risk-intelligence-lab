# Model Card — Risk-Constrained Decision Optimization

**Purpose:** demonstrate how risk limits can be embedded directly into resource-allocation decisions rather than measured only after decisions are made.

**Method:** SLSQP optimization maximizes expected modeled benefit minus an optional risk penalty subject to total budget, per-option caps, non-negativity, and a covariance-based risk limit.

**Limitations:** quadratic covariance risk is stylized; expected benefits are user inputs; no integer/project indivisibility, path dependency, real options, taxes, or causal estimation.
