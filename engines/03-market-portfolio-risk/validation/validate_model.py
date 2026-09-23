from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from engine import PRESETS,simulate_market,summarize
s=PRESETS['Individual Growth Portfolio']; rows=[]
for n in (10000,50000,100000):
 m=summarize(simulate_market(s,n,42)); rows.append((n,m['var_95'],m['es_95'],m['var_99'],m['p95_max_drawdown']))
t='# Validation — Market / Portfolio Risk\n\nSynthetic Individual Growth Portfolio; seed 42.\n\n| Simulations | VaR95 | ES95 | VaR99 | P95 max drawdown |\n|---:|---:|---:|---:|---:|\n'
for n,v,e,v99,d in rows:t+=f'| {n:,} | ${v:,.0f} | ${e:,.0f} | ${v99:,.0f} | {d:.2%} |\n'
t+='\nAutomated checks cover reproducibility, tail-metric ordering, tail attribution reconciliation, correlation-risk monotonicity, and stress-loss aggregation.\n'; (ROOT/'validation'/'VALIDATION.md').write_text(t)
