import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from engine import Option,OptimizationScenario,PRESETS,optimize_allocation,allocation_table,efficient_frontier
COLS=['name','expected_benefit_pct','risk_pct','max_allocation']
def table(s):return pd.DataFrame([[o.name,100*o.expected_benefit_rate,100*o.risk_rate,o.max_allocation] for o in s.options],columns=COLS)
def load(name):s=PRESETS[name];return s.budget,s.risk_limit,s.correlation,table(s)
def parse(f):
 if not isinstance(f,pd.DataFrame):f=pd.DataFrame(f,columns=COLS)
 return tuple(Option(str(r['name']),float(r['expected_benefit_pct'])/100,float(r['risk_pct'])/100,float(r['max_allocation'])) for _,r in f.dropna(subset=['name']).iterrows())
def run(name,budget,limit,corr,frame,aversion):
 s=OptimizationScenario(name,float(budget),float(limit),parse(frame),float(corr));r=optimize_allocation(s,s.risk_limit,float(aversion));t=allocation_table(s,r);front=efficient_frontier(s)
 k=(f"**Allocated:** ${r['spent']:,.0f} / ${s.budget:,.0f} | **Expected modeled benefit:** ${r['expected_benefit']:,.0f} | **Portfolio risk measure:** ${r['risk']:,.0f} / ${s.risk_limit:,.0f} limit")
 f1=go.Figure(go.Bar(x=t.option,y=t.allocation));f1.update_layout(title='Optimized allocation',yaxis_title='Allocation')
 f2=go.Figure(go.Scatter(x=front.realized_risk,y=front.expected_benefit,mode='lines+markers'));f2.add_vline(x=s.risk_limit,line_dash='dash',annotation_text='Current risk limit');f2.update_layout(title='Risk / benefit frontier',xaxis_title='Modeled risk',yaxis_title='Expected benefit')
 f3=go.Figure(go.Bar(x=t.option,y=t.risk_contribution_pct));f3.update_layout(title='Risk contribution by option',yaxis_tickformat='.0%')
 summary=(f"The optimizer allocates **${r['spent']:,.0f}** while keeping the modeled risk measure at **${r['risk']:,.0f}** against a limit of **${s.risk_limit:,.0f}**. "
          "This is a constrained mathematical allocation under the entered assumptions; expected-benefit inputs are not forecasts and the optimizer does not replace human decision judgment.")
 return k,f1,f2,f3,t,front,summary

def build_app():
 d=PRESETS['Growing Small Business']
 with gr.Blocks(title='Risk-Constrained Decision Optimization') as app:
  gr.Markdown('# Risk-Constrained Decision Optimization\nAllocate scarce capital across competing choices while respecting budget, concentration, and modeled risk constraints.')
  with gr.Row():
   with gr.Column(scale=1):
    preset=gr.Dropdown(list(PRESETS),value=d.name,label='Preset');budget=gr.Number(d.budget,label='Available budget');limit=gr.Number(d.risk_limit,label='Risk limit');corr=gr.Slider(-.1,.9,d.correlation,step=.05,label='Option correlation');opts=gr.Dataframe(table(d),headers=COLS,interactive=True,label='Decision options');av=gr.Slider(0,3,0,step=.1,label='Risk aversion penalty');button=gr.Button('Optimize allocation',variant='primary')
   with gr.Column(scale=3):k=gr.Markdown();alloc=gr.Plot();front=gr.Plot()
  with gr.Tab('Risk contribution'):rc=gr.Plot();tab=gr.Dataframe(interactive=False)
  with gr.Tab('Frontier data'):ft=gr.Dataframe(interactive=False)
  with gr.Tab('Decision summary'):summary=gr.Markdown()
  preset.change(load,preset,[budget,limit,corr,opts]);button.click(run,[preset,budget,limit,corr,opts,av],[k,alloc,front,rc,tab,ft,summary])
 return app
