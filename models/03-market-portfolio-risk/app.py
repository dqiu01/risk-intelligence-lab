import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from engine import Asset, PortfolioScenario, PRESETS, simulate_market, summarize, tail_contributions, stress_test, parametric_annual_volatility

COLS=["name","weight_pct","annual_return_pct","annual_volatility_pct"]
def table(s): return pd.DataFrame([[a.name,100*a.weight,100*a.annual_return,100*a.annual_volatility] for a in s.assets],columns=COLS)
def load(name):
    s=PRESETS[name]; return s.portfolio_value,table(s),s.correlation,s.df,s.horizon_days

def parse(frame):
    if not isinstance(frame,pd.DataFrame): frame=pd.DataFrame(frame,columns=COLS)
    return tuple(Asset(str(r["name"]),float(r["weight_pct"])/100,float(r["annual_return_pct"])/100,float(r["annual_volatility_pct"])/100) for _,r in frame.dropna(subset=["name"]).iterrows())

def run(name,value,frame,corr,df,days,sims,seed):
    s=PortfolioScenario(name,float(value),parse(frame),float(corr),float(df),int(days))
    r=simulate_market(s,int(sims),int(seed)); m=summarize(r); c=tail_contributions(r); stress=stress_test(s)
    k=(f"**VaR95:** ${m['var_95']:,.0f} | **ES95:** ${m['es_95']:,.0f} | **VaR99:** ${m['var_99']:,.0f} | "
       f"**P(loss):** {m['loss_probability']:.1%} | **P95 max drawdown:** {m['p95_max_drawdown']:.1%} | **Annualized model vol:** {parametric_annual_volatility(s):.1%}")
    f1=go.Figure(go.Histogram(x=r.losses,nbinsx=70)); f1.add_vline(x=m['var_95'],line_dash='dash',annotation_text='VaR95'); f1.update_layout(title='Portfolio loss distribution',xaxis_title='Loss (negative values are gains)')
    f2=go.Figure(go.Histogram(x=100*r.max_drawdowns,nbinsx=60)); f2.update_layout(title='Maximum drawdown distribution',xaxis_title='Max drawdown %')
    f3=go.Figure(go.Bar(x=c.asset,y=c.tail_contribution)); f3.update_layout(title='95% tail-loss contribution',yaxis_tickformat='.0%')
    summary=(f"The model estimates a 95% loss threshold of **${m['var_95']:,.0f}** and average loss beyond that threshold of **${m['es_95']:,.0f}** over {s.horizon_days} trading days. "
             "Tail contribution shows which holdings dominate severe simulated outcomes. Presets and parameters are synthetic; this is not investment advice.")
    return k,f1,f2,f3,c,stress,summary

def build_app():
    d=PRESETS['Individual Growth Portfolio']
    with gr.Blocks(title='Market / Portfolio Risk') as app:
        gr.Markdown('# Market / Portfolio Risk\nInteractive fat-tail portfolio simulation, VaR/Expected Shortfall, drawdown risk, tail attribution, and stress testing.')
        with gr.Row():
            with gr.Column(scale=1):
                preset=gr.Dropdown(list(PRESETS),value=d.name,label='Preset'); value=gr.Number(d.portfolio_value,label='Portfolio value')
                assets=gr.Dataframe(table(d),headers=COLS,interactive=True,label='Assets')
                corr=gr.Slider(-.1,.9,d.correlation,step=.05,label='Common correlation')
                df=gr.Slider(3,20,d.df,step=1,label='Student-t degrees of freedom')
                days=gr.Slider(1,60,d.horizon_days,step=1,label='Horizon days'); sims=gr.Slider(10000,150000,50000,step=10000,label='Simulations'); seed=gr.Number(42,label='Seed'); button=gr.Button('Run market risk',variant='primary')
            with gr.Column(scale=3): k=gr.Markdown(); dist=gr.Plot(); dd=gr.Plot()
        with gr.Tab('Tail attribution'): contrib_plot=gr.Plot(); contrib=gr.Dataframe(interactive=False)
        with gr.Tab('Stress test'): stress=gr.Dataframe(interactive=False)
        with gr.Tab('Decision summary'): summary=gr.Markdown()
        preset.change(load,preset,[value,assets,corr,df,days])
        button.click(run,[preset,value,assets,corr,df,days,sims,seed],[k,dist,dd,contrib_plot,contrib,stress,summary])
    return app
if __name__=='__main__': build_app().launch()
