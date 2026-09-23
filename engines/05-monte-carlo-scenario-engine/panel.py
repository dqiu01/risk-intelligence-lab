import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from engine import Driver,ScenarioModel,PRESETS,simulate,summarize,driver_importance,stress_table
COLS=['name','base_value','volatility_pct','impact_per_1pct','systemic_loading']
def table(m):return pd.DataFrame([[d.name,d.base_value,d.volatility_pct,d.impact_per_1pct,d.systemic_loading] for d in m.drivers],columns=COLS)
def load(name):m=PRESETS[name];return m.base_outcome,m.target,m.downside_convexity,table(m)
def parse(f):
 if not isinstance(f,pd.DataFrame):f=pd.DataFrame(f,columns=COLS)
 return tuple(Driver(str(r['name']),float(r['base_value']),float(r['volatility_pct']),float(r['impact_per_1pct']),float(r['systemic_loading'])) for _,r in f.dropna(subset=['name']).iterrows())
def run(name,base,target,convexity,frame,sims,seed,stress):
 m=ScenarioModel(name,float(base),float(target),parse(frame),float(convexity));r=simulate(m,int(sims),int(seed),float(stress));s=summarize(r,m.target,m.base_outcome);imp=driver_importance(r);st=stress_table(m)
 k=(f"**Expected outcome:** ${s['expected_outcome']:,.0f} | **P05:** ${s['p05_outcome']:,.0f} | **P95:** ${s['p95_outcome']:,.0f} | **Target miss:** {s['target_miss_probability']:.1%} | **Outcome-at-Risk 95:** ${s['outcome_at_risk_95']:,.0f}")
 f1=go.Figure(go.Histogram(x=r.outcomes,nbinsx=70));f1.add_vline(x=m.target,line_dash='dash',annotation_text='Target');f1.update_layout(title='Outcome distribution',xaxis_title='Modeled outcome')
 f2=go.Figure(go.Bar(x=imp.driver,y=imp.absolute_importance));f2.update_layout(title='Driver importance',yaxis_title='Absolute correlation with outcome')
 summary=(f"The modeled probability of falling below the target of **${m.target:,.0f}** is **{s['target_miss_probability']:.1%}**. The 5th-percentile outcome is **${s['p05_outcome']:,.0f}**. Driver importance measures simulated association with the outcome; it is not causal attribution.")
 return k,f1,f2,imp,st,summary

def build_app():
 d=PRESETS['Growing Small Business']
 with gr.Blocks(title='Monte Carlo Scenario Engine') as app:
  gr.Markdown('# Monte Carlo Scenario Engine\nPropagate multiple uncertain drivers into an outcome distribution, target-miss probability, downside shortfall, and driver sensitivity.')
  with gr.Row():
   with gr.Column(scale=1):
    preset=gr.Dropdown(list(PRESETS),value=d.name,label='Preset');base=gr.Number(d.base_outcome,label='Base annual outcome');target=gr.Number(d.target,label='Target / minimum acceptable outcome');conv=gr.Number(d.downside_convexity,label='Downside convexity penalty');drivers=gr.Dataframe(table(d),headers=COLS,interactive=True,label='Drivers');sims=gr.Slider(10000,150000,50000,step=10000,label='Simulations');seed=gr.Number(42,label='Seed');stress=gr.Slider(-3,3,0,step=.25,label='Systemic factor shift (sigma)');button=gr.Button('Run scenario engine',variant='primary')
   with gr.Column(scale=3):k=gr.Markdown();dist=gr.Plot();importance=gr.Plot()
  with gr.Tab('Driver analytics'):imp=gr.Dataframe(interactive=False)
  with gr.Tab('Stress scenarios'):st=gr.Dataframe(interactive=False)
  with gr.Tab('Decision summary'):summary=gr.Markdown()
  preset.change(load,preset,[base,target,conv,drivers]);button.click(run,[preset,base,target,conv,drivers,sims,seed,stress],[k,dist,importance,imp,st,summary])
 return app
if __name__=='__main__':build_app().launch()
