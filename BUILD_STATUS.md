# Build Status

## Architecture

**Current architecture: one integrated interactive application + eight quantitative engines.**

The previous structure of eight separately launchable mini-apps has been removed.

- Root `app.py`: ✅ single user-facing entry point
- Unified tabbed exploration interface: ✅
- Engine 01 panel adapter: ✅ non-standalone
- Engine 02 panel adapter: ✅ non-standalone
- Engine 03 panel adapter: ✅ non-standalone
- Engine 04 panel adapter: ✅ non-standalone
- Engine 05 panel adapter: ✅ non-standalone
- Engine 06 panel adapter: ✅ non-standalone
- Engine 07 panel adapter: ✅ non-standalone
- Engine 08 panel adapter: ✅ non-standalone

## Engine layer

| # | Engine | Quant engine | Panel adapter | Tests | Validation |
|---:|---|:---:|:---:|:---:|:---:|
| 01 | Risk Exposure & Loss Distribution | ✅ | ✅ | ✅ | ✅ |
| 02 | Liquidity / Cash-Flow-at-Risk | ✅ | ✅ | ✅ | ✅ |
| 03 | Market / Portfolio Risk | ✅ | ✅ | ✅ | ✅ |
| 04 | Credit / Counterparty Risk | ✅ | ✅ | ✅ | ✅ |
| 05 | Monte Carlo Scenario Engine | ✅ | ✅ | ✅ | ✅ |
| 06 | Stress & Reverse Stress | ✅ | ✅ | ✅ | ✅ |
| 07 | Risk-Constrained Optimization | ✅ | ✅ | ✅ | ✅ |
| 08 | Integrated Risk / Dependency | ✅ | ✅ | ✅ | ✅ |

## CI design

CI is intentionally split between:

- **engine validation** — eight independent engine jobs;
- **product integration** — one root-level job that builds the complete interactive laboratory.

This prevents an engine from being treated as its own standalone product while preserving strong quantitative testability.

## Authoritative repository

`dqiu01/risk-intelligence-lab`
