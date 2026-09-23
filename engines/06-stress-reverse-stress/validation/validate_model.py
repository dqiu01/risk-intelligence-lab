from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from engine import PRESETS,scenario_table,reverse_stress,reverse_stress_table
m=PRESETS['Growing Small Business'];s=scenario_table(m);r=reverse_stress(m);rt=reverse_stress_table(m)
t='# Validation — Stress & Reverse Stress Testing\n\nSynthetic Growing Small Business preset.\n\n## Forward scenarios\n\n'+s.to_markdown(index=False)+f"\n\n## Reverse stress\n\nSuccess: {r['success']}  \nLoss at boundary: ${r['loss']:,.0f}  \nRisk capacity: ${m.risk_capacity:,.0f}  \nWeighted distance: {r['distance']:.4f}\n\n"+rt.to_markdown(index=False)+"\n\nAutomated checks verify monotonic loss, boundary feasibility, capacity-distance ordering, ordered forward scenarios, and impossible-threshold handling.\n";(ROOT/'validation'/'VALIDATION.md').write_text(t)
