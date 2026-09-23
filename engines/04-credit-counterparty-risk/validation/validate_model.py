from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from engine import PRESETS,simulate_credit,summarize,analytical_expected_loss
s=PRESETS['Small B2B Receivables'];ana=analytical_expected_loss(s.counterparties);rows=[]
for n in (10000,50000,100000):
 m=summarize(simulate_credit(s.counterparties,n,42,stochastic_lgd=False),s.counterparties,s.reserve);rows.append((n,m['simulated_el'],(m['simulated_el']-ana)/ana,m['var_95'],m['es_95']))
t='# Validation — Credit / Counterparty Risk\n\nSynthetic Small B2B Receivables preset; deterministic LGD for analytical EL comparison.\n\n| Simulations | Simulated EL | Relative error vs analytical EL | VaR95 | ES95 |\n|---:|---:|---:|---:|---:|\n'
for n,e,er,v,es in rows:t+=f'| {n:,} | ${e:,.0f} | {er:.2%} | ${v:,.0f} | ${es:,.0f} |\n'
t+='\nAutomated checks cover reproducibility, analytical-vs-simulated EL, stress monotonicity, tail attribution reconciliation, and concentration metrics.\n';(ROOT/'validation'/'VALIDATION.md').write_text(t)
