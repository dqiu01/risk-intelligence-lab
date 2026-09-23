import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from engine import StressFactor,StressModel,PRESETS,loss_at,scenario_table,reverse_stress,reverse_stress_table,single_factor_breakpoints,two_factor_surface
COLS=['name','max_adverse_change_pct','linear_loss_at_max','quadratic_loss_at_max','plausibility_weight']
def table(m):return pd.DataFrame([[f.name,f.max_adverse_change_pct,f.linear_loss_at_max,f.quadratic_loss_at_max,f.plausibility_weight] for f in m.factors],columns=COLS)
def load(name):m=PRESETS[name];return m.risk_capacity,m.interaction_loss_full,table(m)
def parse(frame):
 if not isinstance(frame,pd.DataFrame):frame=pd.DataFrame(frame,columns=COLS)
 return tuple(StressFactor(str(r['name']),float(r['max_adverse_change_pct']),float(r['linear_loss_at_max']),float(r['quadratic_loss_at_max']),float(r['plausibility_weight'])) for _,r in frame.dropna(subset=['name']).iterrows())
def run(name,capacity,interaction,frame):
 m=StressModel(name,float(capacity),parse(frame),float(interaction));sc=scenario_table(m);rev=reverse_stress(m);rt=reverse_stress_table(m);bp=single_factor_breakpoints(m)
 if rev['success']:
  k=f"**Nearest modeled reverse stress:** distance {rev['distance']:.3f} | **Loss at boundary:** ${rev['loss']:,.0f} | **Risk capacity:** ${m.risk_capacity:,.0f}"
 else:k=f"**Risk capacity is not breached even at all configured maximum shocks.** Maximum modeled loss: ${rev['loss']:,.0f}."
 f1=go.Figure(go.Bar(x=sc.scenario,y=sc.modeled_loss));f1.add_hline(y=m.risk_capacity,line_dash='dash',annotation_text='Risk capacity');f1.update_layout(title='Forward stress scenarios',yaxis_title='Modeled loss')
 f2=go.Figure(go.Bar(x=rt.factor,y=rt.normalized_shock));f2.update_layout(title='Nearest reverse-stress combination',yaxis_title='Fraction of configured maximum shock',yaxis_range=[0,1])
 x,y,z=two_factor_surface(m);f3=go.Figure(go.Heatmap(x=x,y=y,z=z));f3.update_layout(title=f'Loss surface: {m.factors[0].name} vs {m.factors[1].name}',xaxis_title='Factor 1 normalized shock',yaxis_title='Factor 2 normalized shock')
 summary=("Reverse stress asks a different question from ordinary scenario testing: **what is the smallest weighted combination of adverse conditions that reaches the risk-capacity threshold?** "
          "The optimizer minimizes a plausibility-weighted stress distance subject to modeled loss reaching the configured capacity. Results depend directly on the chosen loss functions and maximum shocks.")
 return k,f1,f2,f3,sc,rt,bp,summary

def build_app():
 d=PRESETS['Growing Small Business']
 with gr.Blocks(title='Stress & Reverse Stress Testing') as app:
  gr.Markdown('# Stress & Reverse Stress Testing\nForward scenarios show what a shock does. Reverse stress identifies the smallest modeled shock combination that reaches a defined risk-capacity boundary.')
  with gr.Row():
   with gr.Column(scale=1):
    preset=gr.Dropdown(list(PRESETS),value=d.name,label='Preset');cap=gr.Number(d.risk_capacity,label='Risk capacity');inter=gr.Number(d.interaction_loss_full,label='Full-stress interaction loss');factors=gr.Dataframe(table(d),headers=COLS,interactive=True,label='Stress factors');button=gr.Button('Run stress model',variant='primary')
   with gr.Column(scale=3):k=gr.Markdown();forward=gr.Plot();reverse=gr.Plot()
  with gr.Tab('Two-factor loss surface'):surface=gr.Plot()
  with gr.Tab('Tables'):sc=gr.Dataframe(interactive=False);rt=gr.Dataframe(interactive=False);bp=gr.Dataframe(interactive=False)
  with gr.Tab('Method summary'):summary=gr.Markdown()
  preset.change(load,preset,[cap,inter,factors]);button.click(run,[preset,cap,inter,factors],[k,forward,reverse,surface,sc,rt,bp,summary])
 return app
if __name__=='__main__':build_app().launch()
