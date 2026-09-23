# Model Card — Integrated Risk / Dependency Engine

**Purpose:** demonstrate aggregate risk, diversification, copula-style dependence, correlation stress, and conditional tail contribution across different risk classes.

**Method:** marginal lognormal/gamma losses are linked through a one-factor Gaussian copula. A dependency-scale control changes factor loading while preserving marginal loss distributions.

**Limitations:** one common factor cannot represent all causal dependencies, tail dependence is understated relative to some crisis processes, and synthetic presets are not calibrated to real data.
