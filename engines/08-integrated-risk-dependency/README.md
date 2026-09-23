# Integrated Risk / Dependency Engine

> **Engine component:** This directory is part of the unified Risk Intelligence Lab. `panel.py` is an interface adapter and is not a standalone application. Launch the complete lab from the repository root with `python app.py`.

This model demonstrates why risks cannot always be added independently. Heterogeneous risk distributions are coupled through a common Gaussian factor, producing an integrated total-loss distribution, tail attribution, diversification benefit, and a direct **dependency stress curve**.

## Outputs

Expected aggregate loss, volatility, VaR 95/99, Expected Shortfall 95, reserve-breach probability, sum of stand-alone VaR, diversification benefit, tail contribution, independence-vs-dependency distributions, and VaR/ES sensitivity to dependency strength.

## Method

Each risk has a lognormal or gamma marginal calibrated from mean loss and coefficient of variation. A Gaussian-copula-style common factor generates dependent percentile ranks while preserving each marginal distribution.

```bash
cd ../..
pip install -r requirements.txt
python app.py
```

Synthetic presets only. Dependency structure is stylized and should be calibrated before real use.
