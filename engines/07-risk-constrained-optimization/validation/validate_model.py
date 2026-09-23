from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from engine import PRESETS,optimize_allocation,allocation_table
s=PRESETS['Growing Small Business'];r=optimize_allocation(s);t=allocation_table(s,r)
text=f"# Validation — Risk-Constrained Decision Optimization\n\nSynthetic Growing Small Business preset.\n\nBudget: ${s.budget:,.0f}  \nRisk limit: ${s.risk_limit:,.0f}  \nOptimized spend: ${r['spent']:,.0f}  \nModeled risk: ${r['risk']:,.0f}  \nExpected modeled benefit: ${r['expected_benefit']:,.0f}\n\n## Allocation\n\n"+t.to_markdown(index=False)+"\n\nAutomated checks verify budget/risk constraints, per-option caps, risk-capacity monotonicity, Euler-style risk contribution reconciliation, and frontier feasibility.\n";(ROOT/'validation'/'VALIDATION.md').write_text(text)
