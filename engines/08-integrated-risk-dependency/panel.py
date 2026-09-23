import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from engine import RiskNode,IntegratedScenario,PRESETS,simulate_integrated,summarize,tail_contributions,dependency_comparison
COLS=['name','category','mean_loss','coefficient_of_variation','distribution','common_factor_loading']
def table(s):return pd.DataFrame([[r.name,r.category,r.mean_loss,r.coefficient_of_variation,r.distribution,r.common_factor_loading] for r in s.risks],columns=COLS)
def load(name):s=PRESETS[name];return s.reserve,table(s)
def parse(f):
 if not isinstance(f,pd.DataFrame):f=pd.DataFrame(f,columns=COLS)
 return tuple(RiskNode(str(r['name']),str(r['category']),float(r['mean_loss']),float(r['coefficient_of_variation']),str(r['distribution']),float(r['common_factor_loading'])) for _,r in f.dropna(subset=['name']).iterrows())
def run(name,reserve,frame,scale,sims,seed):
 s=IntegratedScenario(name,parse(frame),float(reserve));r=simulate_integrated(s.risks,int(sims),int(seed),float(scale));m=summarize(r,s.risks,s.reserve);c=tail_contributions(r);curve=dependency_comparison(s,min(int(sims),50000),int(seed));ind=simulate_integrated(s.risks,int(sims),int(seed),0)
 k=(f"**Expected loss:** ${m['expected_loss']:,.0f} | **VaR95:** ${m['var_95']:,.0f} | **ES95:** ${m['es_95']:,.0f} | **Reserve breach:** {m['reserve_breach_probability']:.1%} | **VaR diversification benefit:** ${m['diversification_benefit_var95']:,.0f}")
 f1=go.Figure();f1.add_trace(go.Histogram(x=ind.total_losses,nbinsx=65,name='Independent',opacity=.55));f1.add_trace(go.Histogram(x=r.total_losses,nbinsx=65,name='Selected dependency',opacity=.55));f1.update_layout(title='Integrated loss distribution: independence vs dependency',barmode='overlay',xaxis_title='Total loss')
 f2=go.Figure(go.Bar(x=c.risk,y=c.tail_contribution));f2.update_layout(title='95% tail contribution',yaxis_tickformat='.0%')
 f3=go.Figure();f3.add_trace(go.Scatter(x=curve.correlation_scale,y=curve.var_95,name='VaR95'));f3.add_trace(go.Scatter(x=curve.correlation_scale,y=curve.es_95,name='ES95'));f3.update_layout(title='Dependency stress curve',xaxis_title='Correlation scale',yaxis_title='Loss')
 summary=(f"At the selected dependency scale, modeled VaR95 is **${m['var_95']:,.0f}** and ES95 is **${m['es_95']:,.0f}**. The difference between the sum of stand-alone VaRs and integrated VaR is **${m['diversification_benefit_var95']:,.0f}**. "
          "Diversification can shrink quickly when risks share common drivers, which is the central point of this model.")
 return k,f1,f2,f3,c,curve,summary

def build_app():
 d=PRESETS['Growing Small Business']
 with gr.Blocks(title='Integrated Risk / Dependency Engine') as app:
  gr.Markdown('# Integrated Risk / Dependency Engine\nAggregate heterogeneous risk distributions with a Gaussian-copula-style common factor, quantify diversification, and stress dependency itself.')
  with gr.Row():
   with gr.Column(scale=1):
    preset=gr.Dropdown(list(PRESETS),value=d.name,label='Preset');reserve=gr.Number(d.reserve,label='Reserve / loss capacity');risks=gr.Dataframe(table(d),headers=COLS,interactive=True,label='Risk nodes');scale=gr.Slider(0,1.5,1,step=.05,label='Dependency scale');sims=gr.Slider(10000,150000,50000,step=10000,label='Simulations');seed=gr.Number(42,label='Seed');button=gr.Button('Run integrated risk model',variant='primary')
   with gr.Column(scale=3):k=gr.Markdown();dist=gr.Plot();tail=gr.Plot()
  with gr.Tab('Dependency stress'):curve=gr.Plot();curve_table=gr.Dataframe(interactive=False)
  with gr.Tab('Tail contribution'):ct=gr.Dataframe(interactive=False)
  with gr.Tab('Decision summary'):summary=gr.Markdown()
  preset.change(load,preset,[reserve,risks]);button.click(run,[preset,reserve,risks,scale,sims,seed],[k,dist,tail,curve,ct,curve_table,summary])
 return app
