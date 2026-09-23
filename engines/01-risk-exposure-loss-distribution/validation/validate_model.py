from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from risk_model import analyze, load_scenario  # noqa: E402
from risk_model.severity import analytical_severity_mean  # noqa: E402


def convergence_table(scenario, seed=42):
    analytical = sum(r.annual_frequency * analytical_severity_mean(r) for r in scenario.risks)
    rows = []
    for n in (10_000, 50_000, 100_000, 250_000):
        analysis = analyze(scenario.risks, scenario.reserve, scenario.risk_tolerance, n, seed)
        rows.append({
            "simulations": n,
            "simulated_expected_loss": analysis.metrics.expected_loss,
            "analytical_independent_mean_reference": analytical,
            "relative_error_vs_reference": (analysis.metrics.expected_loss - analytical) / analytical,
            "var_95": analysis.metrics.var_95,
            "es_95": analysis.metrics.es_95,
            "reserve_breach_probability": analysis.metrics.reserve_breach_probability,
        })
    return pd.DataFrame(rows)


def main():
    scenario = load_scenario(ROOT / "scenarios" / "small_business.yaml")
    table = convergence_table(scenario)
    table.to_csv(ROOT / "validation" / "convergence.csv", index=False)

    final = analyze(scenario.risks, scenario.reserve, scenario.risk_tolerance, 250_000, 42)

    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(final.result.total_losses, bins=80, density=True, alpha=0.8)
    ax.axvline(final.metrics.expected_loss, linestyle="--", label="Expected loss")
    ax.axvline(final.metrics.var_95, linestyle="--", label="VaR 95")
    ax.axvline(final.metrics.es_95, linestyle=":", label="Expected Shortfall 95")
    ax.axvline(scenario.reserve, linestyle="-.", label="Reserve")
    ax.set_title("Growing Small Business — Modeled Annual Loss Distribution")
    ax.set_xlabel("Annual loss")
    ax.set_ylabel("Density")
    ax.legend()
    fig.tight_layout()
    fig.savefig(assets / "loss-distribution-validation.png", dpi=160)
    plt.close(fig)

    report = "# Model Validation Report\n\n"
    report += "This report is generated from the synthetic **Growing Small Business** preset. It validates numerical behavior; it does not claim real-world calibration.\n\n"
    report += "## High-precision simulation\n\n"
    report += (
        f"- Simulations: 250,000\n"
        f"- Seed: 42\n"
        f"- Expected annual loss: ${final.metrics.expected_loss:,.0f}\n"
        f"- VaR 95: ${final.metrics.var_95:,.0f}\n"
        f"- VaR 99: ${final.metrics.var_99:,.0f}\n"
        f"- Expected Shortfall 95: ${final.metrics.es_95:,.0f}\n"
        f"- Reserve breach probability: {final.metrics.reserve_breach_probability:.2%}\n\n"
    )
    report += "## Convergence table\n\n"
    report += table.to_markdown(index=False, floatfmt=".6f")
    report += "\n"
    (ROOT / "validation" / "VALIDATION.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
