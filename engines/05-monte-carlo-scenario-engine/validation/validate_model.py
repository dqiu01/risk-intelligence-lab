from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from engine import PRESETS,simulate,summarize
m=PRESETS['Growing Small Business'];rows=[]
for n in (10000,50000,100000):
 s=summarize(simulate(m,n,42),m.target,m.base_outcome);rows.append((n,s['expected_outcome'],s['p05_outcome'],s['target_miss_probability'],s['outcome_at_risk_95']))
t='# Validation — Monte Carlo Scenario Engine\n\nSynthetic Growing Small Business preset; seed 42.\n\n| Simulations | Expected outcome | P05 | Target miss | Outcome-at-Risk 95 |\n|---:|---:|---:|---:|---:|\n'
for n,e,p,b,o in rows:t+=f'| {n:,} | ${e:,.0f} | ${p:,.0f} | {b:.2%} | ${o:,.0f} |\n'
t+='\nChecks cover reproducibility, probability bounds, adverse systemic stress, driver-importance bounds, and ordered deterministic stress scenarios.\n';(ROOT/'validation'/'VALIDATION.md').write_text(t)
