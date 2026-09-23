# Build Status

## Product architecture

**Current design: one browser interface + eight embedded quantitative engines.**

- Browser interface: ✅ implemented in `web/`
- Engine navigation: ✅
- Scenario presets: ✅
- Editable engine-specific controls: ✅
- Dynamic KPI cards: ✅
- Plotly distributions / contribution charts / stress curves / frontiers: ✅
- Browser-to-Python bridge: ✅
- Python engines executed through Pyodide: ✅
- Standalone engine applications: **removed**
- Gradio interface layer: **removed**
- Public deployment workflow: ✅ prepared
- GitHub Pages repository setting: ⏳ one-time enablement still required

## Engine layer

| # | Engine | Quantitative engine | Tests | Validation |
|---:|---|:---:|:---:|:---:|
| 01 | Risk Exposure & Loss Distribution | ✅ | ✅ | ✅ |
| 02 | Liquidity / Cash-Flow-at-Risk | ✅ | ✅ | ✅ |
| 03 | Market / Portfolio Risk | ✅ | ✅ | ✅ |
| 04 | Credit / Counterparty Risk | ✅ | ✅ | ✅ |
| 05 | Monte Carlo Scenario Engine | ✅ | ✅ | ✅ |
| 06 | Stress & Reverse Stress | ✅ | ✅ | ✅ |
| 07 | Risk-Constrained Optimization | ✅ | ✅ | ✅ |
| 08 | Integrated Risk / Dependency | ✅ | ✅ | ✅ |

## Interface verification

The browser CI verifies:

- `web/index.html`, `web/styles.css`, `web/app.js`, and `web/bridge.py` exist;
- JavaScript parses successfully;
- the Python browser bridge compiles;
- all eight engine source trees required by the browser bundle exist;
- the deployable static bundle assembles successfully.

## Authoritative repository

`dqiu01/risk-intelligence-lab`
