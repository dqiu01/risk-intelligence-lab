from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parent

ENGINES = [
    ("Overview", None),
    ("Loss Distribution", "01-risk-exposure-loss-distribution"),
    ("Liquidity / Cash-Flow-at-Risk", "02-liquidity-cashflow-risk"),
    ("Market / Portfolio Risk", "03-market-portfolio-risk"),
    ("Credit / Counterparty Risk", "04-credit-counterparty-risk"),
    ("Monte Carlo Scenario Engine", "05-monte-carlo-scenario-engine"),
    ("Stress & Reverse Stress", "06-stress-reverse-stress"),
    ("Risk-Constrained Optimization", "07-risk-constrained-optimization"),
    ("Integrated Risk / Dependency", "08-integrated-risk-dependency"),
]


def _load_panel(slug: str, index: int):
    engine_dir = ROOT / "engines" / slug
    panel_path = engine_dir / "panel.py"
    module_name = f"risk_intelligence_panel_{index}"

    # Engine packages intentionally use short local imports such as engine.
    # Load each panel in its own path context and clear that import name between
    # panels so no engine can accidentally bind to another engine module.
    sys.modules.pop("engine", None)
    sys.path.insert(0, str(engine_dir))
    try:
        spec = importlib.util.spec_from_file_location(module_name, panel_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load engine panel: {panel_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(engine_dir))


def _overview() -> gr.Blocks:
    with gr.Blocks() as overview:
        gr.Markdown(
            """
# Risk Intelligence Lab

**One interactive laboratory powered by eight quantitative risk engines.**

Use the tabs above to move between risk questions without leaving the application.
Each tab is an interface adapter connected to a quantitative engine underneath it;
the engines are not separate products or standalone applications.

### Explore the lab

1. **Loss Distribution** — frequency/severity risk, aggregate loss, tail risk, reserve adequacy, mitigation.
2. **Liquidity / Cash-Flow-at-Risk** — stochastic cash paths, liquidity breach, insolvency, buffer sizing.
3. **Market / Portfolio Risk** — fat-tail portfolio losses, VaR/ES, drawdowns, attribution, stress.
4. **Credit / Counterparty Risk** — PD/LGD/EAD, correlated defaults, concentration, tail loss.
5. **Monte Carlo Scenario Engine** — propagate uncertain business or personal drivers into outcome distributions.
6. **Stress & Reverse Stress** — test shocks and solve backward for conditions that breach risk capacity.
7. **Risk-Constrained Optimization** — allocate scarce resources while respecting explicit risk constraints.
8. **Integrated Risk / Dependency** — aggregate heterogeneous risks and explore diversification versus dependency.

The common design principle is:

**change assumptions → run an engine → inspect the visual result → understand the decision implication**
            """
        )
    return overview


def build_app() -> gr.Blocks:
    interfaces = [_overview()]
    tab_names = ["Overview"]

    for index, (name, slug) in enumerate(ENGINES[1:], start=1):
        panel = _load_panel(slug, index)
        interfaces.append(panel.build_app())
        tab_names.append(name)

    return gr.TabbedInterface(
        interface_list=interfaces,
        tab_names=tab_names,
        title="Risk Intelligence Lab",
    )


if __name__ == "__main__":
    build_app().launch()
