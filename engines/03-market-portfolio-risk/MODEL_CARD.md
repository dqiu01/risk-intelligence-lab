# Model Card — Market / Portfolio Risk

**Purpose:** demonstrate portfolio risk aggregation, fat-tail simulation, VaR/Expected Shortfall, drawdown analysis, attribution, and stress testing.

**Method:** correlated Student-t daily returns with user-defined annual return/volatility and an equicorrelation structure. Portfolio returns are daily rebalanced for the simulation horizon.

**Limitations:** no volatility clustering, regime switching, liquidity impact, options convexity, or empirical calibration in the presets. Tail contribution uses a linear asset-loss approximation within simulated portfolio tail states.
