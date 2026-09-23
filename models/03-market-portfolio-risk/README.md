# Market / Portfolio Risk

A fat-tail market-risk simulator for personal portfolios, operating reserves, treasuries, and institutional multi-asset allocations. It uses correlated Student-t returns to make tail behavior visible rather than assuming purely Gaussian markets.

## Outputs

VaR 95/99, Expected Shortfall 95/99, loss probability, simulated maximum drawdown, tail-loss contribution by asset, parametric portfolio volatility, and deterministic stress P&L.

## Interface

Edit weights, expected returns, volatilities, common correlation, tail thickness, horizon, portfolio value, and simulation count. Visualize the P&L distribution, drawdown distribution, tail attribution, and stress results.

```bash
pip install -r requirements.txt
python app.py
```

Synthetic inputs only; not investment advice or a forecast.
