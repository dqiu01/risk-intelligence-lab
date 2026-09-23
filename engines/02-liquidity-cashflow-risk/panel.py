from __future__ import annotations
import gradio as gr
import plotly.graph_objects as go
from engine import PRESETS, LiquidityScenario, simulate_liquidity, summarize, percentile_paths, compare_actions


def money(x):
    return f"${x:,.0f}"


def load(name):
    s = PRESETS[name]
    return s.starting_cash, s.monthly_income, s.fixed_cost, s.variable_cost_pct*100, s.debt_service, s.minimum_cash, s.income_volatility*100, s.cost_volatility*100, s.collection_delay_pct*100


def run(name, starting_cash, income, fixed, variable_pct, debt, minimum, income_vol, cost_vol, delay, sims, seed, income_shock, cost_shock):
    s = LiquidityScenario(name, float(starting_cash), float(income), float(fixed), float(variable_pct)/100, float(debt), float(minimum), float(income_vol)/100, float(cost_vol)/100, float(delay)/100)
    r = simulate_liquidity(s, int(sims), int(seed), income_shock, cost_shock)
    m = summarize(r, s)
    paths = percentile_paths(r)
    kpi = " | ".join([
        f"**Expected ending cash:** {money(m['expected_ending_cash'])}",
        f"**Cash-Flow-at-Risk 95:** {money(m['cashflow_at_risk_95'])}",
        f"**Breach probability:** {m['liquidity_breach_probability']:.1%}",
        f"**Insolvency probability:** {m['insolvency_probability']:.1%}",
        f"**Additional buffer for 95%:** {money(m['required_additional_buffer_95'])}",
    ])
    f1 = go.Figure(go.Histogram(x=r.ending_cash, nbinsx=60))
    f1.add_vline(x=s.minimum_cash, line_dash="dash", annotation_text="Minimum cash")
    f1.update_layout(title="Ending cash distribution", xaxis_title="Ending cash")
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=paths.month, y=paths.p90, name="P90"))
    f2.add_trace(go.Scatter(x=paths.month, y=paths["median"], name="Median"))
    f2.add_trace(go.Scatter(x=paths.month, y=paths.p10, name="P10", fill="tonexty"))
    f2.add_hline(y=s.minimum_cash, line_dash="dash", annotation_text="Minimum")
    f2.update_layout(title="Liquidity path envelope", xaxis_title="Month", yaxis_title="Cash")
    actions = compare_actions(s, min(int(sims), 50000), int(seed))
    f3 = go.Figure(go.Bar(x=actions.action, y=actions.liquidity_breach_probability))
    f3.update_layout(title="Modeled liquidity breach by action", yaxis_tickformat=".0%")
    interpretation = f"Based on the entered assumptions, the modeled probability of falling below the minimum cash level is **{m['liquidity_breach_probability']:.1%}**. A 95% modeled liquidity buffer would require approximately **{money(m['required_additional_buffer_95'])}** of additional starting cash beyond the current setup. These are scenario results, not forecasts."
    return kpi, f1, f2, f3, actions, interpretation


def build_app():
    d = PRESETS["Growing Small Business"]
    with gr.Blocks(title="Liquidity / Cash-Flow-at-Risk") as app:
        gr.Markdown("# Liquidity / Cash-Flow-at-Risk\nModel cash-path uncertainty, reserve adequacy, runway stress, and liquidity interventions across personal and organizational scales.")
        with gr.Row():
            with gr.Column(scale=1):
                preset=gr.Dropdown(list(PRESETS), value=d.name, label="Preset")
                start=gr.Number(d.starting_cash,label="Starting cash")
                income=gr.Number(d.monthly_income,label="Monthly income / revenue")
                fixed=gr.Number(d.fixed_cost,label="Monthly fixed cost")
                var=gr.Slider(0,100,d.variable_cost_pct*100,label="Variable cost % of income")
                debt=gr.Number(d.debt_service,label="Monthly debt service")
                minimum=gr.Number(d.minimum_cash,label="Minimum cash requirement")
                iv=gr.Slider(0,100,d.income_volatility*100,label="Income volatility %")
                cv=gr.Slider(0,100,d.cost_volatility*100,label="Cost volatility %")
                delay=gr.Slider(0,100,d.collection_delay_pct*100,label="Delayed collections %")
                sims=gr.Slider(10000,150000,50000,step=10000,label="Simulations")
                seed=gr.Number(42,label="Seed")
                income_shock=gr.Slider(-50,50,0,step=5,label="Income shock %")
                cost_shock=gr.Slider(-30,50,0,step=5,label="Cost shock %")
                button=gr.Button("Run liquidity model",variant="primary")
            with gr.Column(scale=3):
                kpi=gr.Markdown()
                dist=gr.Plot()
                path=gr.Plot()
        with gr.Tab("Action comparison"):
            action_plot=gr.Plot(); action_table=gr.Dataframe(interactive=False)
        with gr.Tab("Decision summary"):
            summary=gr.Markdown()
        preset.change(load,preset,[start,income,fixed,var,debt,minimum,iv,cv,delay])
        button.click(run,[preset,start,income,fixed,var,debt,minimum,iv,cv,delay,sims,seed,income_shock,cost_shock],[kpi,dist,path,action_plot,action_table,summary])
    return app
