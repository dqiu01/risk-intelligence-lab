import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from engine import Counterparty,CreditScenario,PRESETS,simulate_credit,summarize,contributions,concentration_metrics,stress_grid
COLS=['name','sector','ead','pd_pct','lgd_pct','asset_correlation_pct']
def table(s):return pd.DataFrame([[c.name,c.sector,c.ead,100*c.pd,100*c.lgd,100*c.asset_correlation] for c in s.counterparties],columns=COLS)
def load(name):s=PRESETS[name];return s.reserve,table(s)
def parse(f):
 if not isinstance(f,pd.DataFrame):f=pd.DataFrame(f,columns=COLS)
 return tuple(Counterparty(str(r['name']),str(r['sector']),float(r['ead']),float(r['pd_pct'])/100,float(r['lgd_pct'])/100,float(r['asset_correlation_pct'])/100) for _,r in f.dropna(subset=['name']).iterrows())
def run(name,reserve,frame,sims,seed,pdm,lgdadd):
 cps=parse(frame); r=simulate_credit(cps,int(sims),int(seed),float(pdm),float(lgdadd)/100); m=summarize(r,cps,float(reserve)); c=contributions(r,cps); cm=concentration_metrics(cps); grid=stress_grid(cps,float(reserve),min(int(sims),30000),int(seed))
 k=(f"**Expected loss:** ${m['simulated_el']:,.0f} | **Unexpected loss (SD):** ${m['unexpected_loss']:,.0f} | **VaR95:** ${m['var_95']:,.0f} | **ES95:** ${m['es_95']:,.0f} | **Reserve breach:** {m['reserve_breach_probability']:.1%} | **Largest EAD:** {cm['largest_exposure_share']:.1%}")
 f1=go.Figure(go.Histogram(x=r.total_losses,nbinsx=60));f1.add_vline(x=float(reserve),line_dash='dash',annotation_text='Reserve');f1.update_layout(title='Credit loss distribution',xaxis_title='Loss')
 f2=go.Figure(go.Bar(x=c.counterparty,y=c.tail_contribution));f2.update_layout(title='95% tail-loss contribution',yaxis_tickformat='.0%')
 f3=go.Figure(go.Bar(x=c.counterparty,y=c.ead));f3.update_layout(title='Exposure concentration',yaxis_title='EAD')
 summary=(f"Total modeled exposure at default is **${cm['total_ead']:,.0f}**. The portfolio's effective counterparty count is **{cm['effective_counterparties']:.1f}** after concentration. "
          f"Under the selected assumptions, the reserve-breach probability is **{m['reserve_breach_probability']:.1%}**. Results are synthetic scenario estimates, not credit ratings or lending advice.")
 return k,f1,f2,f3,c,grid,summary

def build_app():
 d=PRESETS['Small B2B Receivables']
 with gr.Blocks(title='Credit / Counterparty Risk') as app:
  gr.Markdown('# Credit / Counterparty Risk\nOne-factor/sector-correlated default simulation with PD, LGD, EAD, concentration, tail attribution, and stress testing.')
  with gr.Row():
   with gr.Column(scale=1):
    preset=gr.Dropdown(list(PRESETS),value=d.name,label='Preset');reserve=gr.Number(d.reserve,label='Loss reserve');cps=gr.Dataframe(table(d),headers=COLS,interactive=True,label='Counterparties');sims=gr.Slider(10000,150000,50000,step=10000,label='Simulations');seed=gr.Number(42,label='Seed');pdm=gr.Slider(.5,4,1,step=.1,label='PD multiplier');lgd=gr.Slider(-20,30,0,step=1,label='LGD stress, percentage points');button=gr.Button('Run credit model',variant='primary')
   with gr.Column(scale=3):k=gr.Markdown();dist=gr.Plot();tail=gr.Plot()
  with gr.Tab('Concentration'):conc=gr.Plot();ct=gr.Dataframe(interactive=False)
  with gr.Tab('Stress grid'):grid=gr.Dataframe(interactive=False)
  with gr.Tab('Decision summary'):summary=gr.Markdown()
  preset.change(load,preset,[reserve,cps]);button.click(run,[preset,reserve,cps,sims,seed,pdm,lgd],[k,dist,tail,conc,ct,grid,summary])
 return app
