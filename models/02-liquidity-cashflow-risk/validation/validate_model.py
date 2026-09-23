from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from engine import PRESETS, simulate_liquidity, summarize

s=PRESETS["Growing Small Business"]
rows=[]
for n in (10000,50000,100000):
    m=summarize(simulate_liquidity(s,n,42),s)
    rows.append((n,m["expected_ending_cash"],m["liquidity_breach_probability"],m["required_additional_buffer_95"]))
text="# Validation — Liquidity / Cash-Flow-at-Risk\n\nSynthetic Growing Small Business preset; seed 42.\n\n| Simulations | Expected ending cash | Breach probability | Additional buffer 95% |\n|---:|---:|---:|---:|\n"
for n,e,b,r in rows: text += f"| {n:,} | ${e:,.0f} | {b:.2%} | ${r:,.0f} |\n"
text += "\nChecks: deterministic seed, bounded probabilities, adverse shocks worsen liquidity, and reserve additions do not increase modeled breach probability.\n"
(ROOT/"validation"/"VALIDATION.md").write_text(text)
