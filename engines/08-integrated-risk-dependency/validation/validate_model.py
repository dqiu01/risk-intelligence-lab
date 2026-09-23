from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from engine import PRESETS,dependency_comparison,simulate_integrated,summarize
s=PRESETS['Growing Small Business'];curve=dependency_comparison(s,60000,42);r=simulate_integrated(s.risks,100000,42,1);m=summarize(r,s.risks,s.reserve)
t=f"# Validation — Integrated Risk / Dependency Engine\n\nSynthetic Growing Small Business preset.\n\nExpected loss: ${m['expected_loss']:,.0f}  \nVaR95: ${m['var_95']:,.0f}  \nES95: ${m['es_95']:,.0f}  \nVaR diversification benefit: ${m['diversification_benefit_var95']:,.0f}\n\n## Dependency curve\n\n"+curve.to_markdown(index=False)+"\n\nAutomated checks cover reproducibility, marginal-mean preservation, tail-contribution reconciliation, dependency-driven volatility/ES increase, and dependency-curve generation.\n";(ROOT/'validation'/'VALIDATION.md').write_text(t)
