const ENGINES = [
  {id:"01", short:"Loss Distribution", title:"Risk Exposure & Loss Distribution", desc:"Model event frequency and severity, aggregate losses, tail risk, reserve adequacy, and stress effects.", controls:[
    {key:"reserve",label:"Available reserve",type:"number",step:1000,format:"currency"},
    {key:"risk_tolerance",label:"Risk tolerance",type:"number",step:1000,format:"currency"},
    {key:"frequency_shock_pct",label:"Frequency shock",type:"range",min:-50,max:150,step:5,format:"percentRaw"},
    {key:"severity_shock_pct",label:"Severity shock",type:"range",min:-50,max:150,step:5,format:"percentRaw"},
    {key:"simulations",label:"Monte Carlo runs",type:"range",min:5000,max:30000,step:5000,format:"integer"}
  ]},
  {id:"02", short:"Liquidity", title:"Liquidity / Cash-Flow-at-Risk", desc:"Simulate future cash paths and explore liquidity breach, insolvency, and buffer requirements.", controls:[
    {key:"starting_cash",label:"Starting cash",type:"number",step:1000,format:"currency"},
    {key:"minimum_cash",label:"Minimum cash threshold",type:"number",step:1000,format:"currency"},
    {key:"income_shock_pct",label:"Income / revenue shock",type:"range",min:-50,max:50,step:5,format:"percentRaw"},
    {key:"cost_shock_pct",label:"Cost shock",type:"range",min:-30,max:50,step:5,format:"percentRaw"},
    {key:"simulations",label:"Simulation paths",type:"range",min:5000,max:30000,step:5000,format:"integer"}
  ]},
  {id:"03", short:"Market Risk", title:"Market / Portfolio Risk", desc:"Explore fat-tail portfolio losses, VaR, Expected Shortfall, drawdown, concentration, and correlation.", controls:[
    {key:"portfolio_value",label:"Portfolio value",type:"number",step:1000,format:"currency"},
    {key:"correlation",label:"Common correlation",type:"range",min:-0.1,max:0.9,step:0.05,format:"decimal"},
    {key:"horizon_days",label:"Risk horizon (days)",type:"range",min:1,max:60,step:1,format:"integer"},
    {key:"simulations",label:"Simulation paths",type:"range",min:5000,max:25000,step:5000,format:"integer"}
  ]},
  {id:"04", short:"Credit Risk", title:"Credit / Counterparty Risk", desc:"Stress PD, LGD and reserves while observing expected loss, tail loss, and counterparty contribution.", controls:[
    {key:"reserve",label:"Loss reserve",type:"number",step:1000,format:"currency"},
    {key:"pd_multiplier",label:"PD multiplier",type:"range",min:0.5,max:4,step:0.1,format:"multiple"},
    {key:"lgd_add_pct",label:"LGD stress",type:"range",min:-20,max:30,step:1,format:"percentRaw"},
    {key:"simulations",label:"Simulation paths",type:"range",min:5000,max:30000,step:5000,format:"integer"}
  ]},
  {id:"05", short:"Scenarios", title:"Monte Carlo Scenario Engine", desc:"Propagate correlated demand, pricing, cost, rate, and other continuous drivers into outcome distributions.", controls:[
    {key:"base_outcome",label:"Base annual outcome",type:"number",step:1000,format:"currency"},
    {key:"target",label:"Target / minimum outcome",type:"number",step:1000,format:"currency"},
    {key:"systemic_stress",label:"Systemic shift (sigma)",type:"range",min:-3,max:3,step:0.25,format:"decimal"},
    {key:"simulations",label:"Simulation paths",type:"range",min:5000,max:30000,step:5000,format:"integer"}
  ]},
  {id:"06", short:"Stress Testing", title:"Stress & Reverse Stress Testing", desc:"See what predefined shocks do, then solve backward for the nearest adverse combination that breaches risk capacity.", controls:[
    {key:"risk_capacity",label:"Risk capacity",type:"number",step:1000,format:"currency"}
  ]},
  {id:"07", short:"Optimization", title:"Risk-Constrained Decision Optimization", desc:"Allocate scarce resources while enforcing budget, option-cap, correlation, and portfolio risk constraints.", controls:[
    {key:"budget",label:"Available budget",type:"number",step:1000,format:"currency"},
    {key:"risk_limit",label:"Risk limit",type:"number",step:1000,format:"currency"},
    {key:"risk_aversion",label:"Risk-aversion penalty",type:"range",min:0,max:3,step:0.1,format:"decimal"}
  ]},
  {id:"08", short:"Integrated Risk", title:"Integrated Risk / Dependency", desc:"Aggregate heterogeneous risk distributions and explore how dependence changes diversification and tail exposure.", controls:[
    {key:"reserve",label:"Reserve / loss capacity",type:"number",step:1000,format:"currency"},
    {key:"dependency_scale",label:"Dependency scale",type:"range",min:0,max:1.5,step:0.05,format:"decimal"},
    {key:"simulations",label:"Simulation paths",type:"range",min:5000,max:25000,step:5000,format:"integer"}
  ]}
];

const state = {pyodide:null, current:null, defaults:{}, ready:false};

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

function setProgress(pct, text){
  $("#boot-progress").style.width = pct + "%";
  $("#boot-text").textContent = text;
}

function fmt(value, format){
  if(format === "currency"){
    const a=Math.abs(value);
    if(a>=1e9) return (value<0?"-":"")+"$"+(a/1e9).toFixed(2)+"B";
    if(a>=1e6) return (value<0?"-":"")+"$"+(a/1e6).toFixed(2)+"M";
    if(a>=1e3) return (value<0?"-":"")+"$"+(a/1e3).toFixed(1)+"K";
    return (value<0?"-":"")+"$"+a.toLocaleString(undefined,{maximumFractionDigits:0});
  }
  if(format === "percent") return (100*value).toFixed(1)+"%";
  if(format === "percentRaw") return Number(value).toFixed(0)+"%";
  if(format === "multiple") return Number(value).toFixed(1)+"×";
  if(format === "integer") return Math.round(value).toLocaleString();
  return Number(value).toLocaleString(undefined,{maximumFractionDigits:3});
}

function renderNavigation(){
  const nav=$("#engine-nav"), grid=$("#overview-grid");
  ENGINES.forEach((e,i)=>{
    const btn=document.createElement("button");
    btn.className="nav-item";
    btn.dataset.engine=e.id;
    btn.innerHTML=`<span class="nav-num">${e.id}</span><span><b>${e.short}</b><small>${e.title}</small></span>`;
    btn.addEventListener("click",()=>openEngine(e.id));
    nav.appendChild(btn);

    const tile=document.createElement("article");
    tile.className="engine-tile";
    tile.innerHTML=`<span class="num">ENGINE ${e.id}</span><h3>${e.title}</h3><p>${e.desc}</p><span class="go">Explore engine →</span>`;
    tile.addEventListener("click",()=>openEngine(e.id));
    grid.appendChild(tile);
  });
  $("#start-exploring").addEventListener("click",()=>openEngine("01"));
  document.querySelector('[data-view="overview"]').addEventListener("click",showOverview);
}

function showOverview(){
  state.current=null;
  $$(".nav-item").forEach(x=>x.classList.remove("active"));
  document.querySelector('[data-view="overview"]').classList.add("active");
  $("#overview-view").classList.add("active");
  $("#engine-view").classList.remove("active");
  window.scrollTo({top:0,behavior:"smooth"});
}

async function pyCall(expr, vars={}){
  for(const [k,v] of Object.entries(vars)) state.pyodide.globals.set(k,v);
  return await state.pyodide.runPythonAsync(expr);
}

async function getPresets(id){
  const raw=await pyCall("bridge.presets_json(engine_id)",{engine_id:id});
  return JSON.parse(raw);
}

async function getDefaults(id,preset){
  const raw=await pyCall("bridge.defaults_json(engine_id, preset_name)",{engine_id:id,preset_name:preset});
  return JSON.parse(raw);
}

function controlValueLabel(def,value){
  if(def.format==="currency") return fmt(Number(value),"currency");
  if(def.format==="percentRaw") return fmt(Number(value),"percentRaw");
  if(def.format==="multiple") return fmt(Number(value),"multiple");
  if(def.format==="integer") return fmt(Number(value),"integer");
  return Number(value).toFixed(def.step && def.step<1 ? 2 : 1);
}

function buildControls(engine, defaults){
  const root=$("#dynamic-controls");
  root.innerHTML="";
  engine.controls.forEach(def=>{
    const label=document.createElement("label");
    label.className="field";
    const val=defaults[def.key];
    const head=document.createElement("span");
    const title=document.createElement("span");
    title.textContent=def.label;
    const out=document.createElement("output");
    out.id="out-"+def.key;
    out.textContent=controlValueLabel(def,val);
    head.append(title,out);
    label.appendChild(head);

    const input=document.createElement("input");
    input.dataset.key=def.key;
    input.dataset.format=def.format||"number";
    if(def.type==="range"){
      input.type="range"; input.min=def.min; input.max=def.max; input.step=def.step; input.value=val;
      input.addEventListener("input",()=>out.textContent=controlValueLabel(def,input.value));
    }else{
      input.type="number"; input.step=def.step||"any"; input.value=val;
      input.addEventListener("input",()=>out.textContent=controlValueLabel(def,input.value));
    }
    label.appendChild(input); root.appendChild(label);
  });
}

async function openEngine(id){
  if(!state.ready) return;
  const engine=ENGINES.find(x=>x.id===id);
  state.current=engine;
  $$(".nav-item").forEach(x=>x.classList.remove("active"));
  const active=document.querySelector(`[data-engine="${id}"]`);
  if(active) active.classList.add("active");
  $("#overview-view").classList.remove("active");
  $("#engine-view").classList.add("active");
  $("#engine-kicker").textContent="ENGINE "+engine.id;
  $("#engine-title").textContent=engine.title;
  $("#engine-description").textContent=engine.desc;
  $("#engine-id").textContent=engine.id;

  const presets=await getPresets(id);
  const select=$("#preset-select");
  select.innerHTML=presets.map(x=>`<option>${x}</option>`).join("");
  const preset=presets.includes("Growing Small Business") ? "Growing Small Business" : presets[0];
  select.value=preset;
  state.defaults=await getDefaults(id,preset);
  buildControls(engine,state.defaults);
  clearResults();
  await runCurrent();
  window.scrollTo({top:0,behavior:"smooth"});
}

function clearResults(){
  $("#kpi-grid").innerHTML="";
  $("#interpretation").textContent="Run the engine to calculate this scenario.";
  $("#model-note").textContent="";
  Plotly.purge("chart-1"); Plotly.purge("chart-2");
}

function readControls(){
  const c={};
  $$("#dynamic-controls input").forEach(input=>c[input.dataset.key]=Number(input.value));
  return c;
}

async function resetControls(){
  if(!state.current) return;
  const preset=$("#preset-select").value;
  state.defaults=await getDefaults(state.current.id,preset);
  buildControls(state.current,state.defaults);
  await runCurrent();
}

function plotChart(targetId, chart){
  const traces=chart.traces.map(t=>({
    x:t.x,y:t.y,name:t.name,type:t.type==="line"?"scatter":"bar",
    mode:t.type==="line"?"lines+markers":undefined,
    marker:t.type==="bar"?{line:{width:0}}:undefined,
    line:t.type==="line"?{width:2.5}:undefined,
    opacity:t.type==="bar"?.82:1
  }));
  const layout={
    title:{text:chart.title,font:{size:15,color:"#dcebf5"},x:.04},
    paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",
    font:{family:"Inter, system-ui",size:10,color:"#8da3b5"},
    margin:{l:58,r:20,t:50,b:65},
    xaxis:{title:chart.x_label,gridcolor:"#1b2b38",zerolinecolor:"#314657",tickfont:{size:9}},
    yaxis:{title:chart.y_label,gridcolor:"#1b2b38",zerolinecolor:"#314657",tickfont:{size:9}},
    legend:{orientation:"h",x:0,y:1.13,font:{size:9}},
    hoverlabel:{bgcolor:"#132432",bordercolor:"#34566d",font:{color:"#fff"}},
    bargap:.08,barmode:"group"
  };
  Plotly.react(targetId,traces,layout,{responsive:true,displaylogo:false,modeBarButtonsToRemove:["lasso2d","select2d"]});
}

async function runCurrent(){
  if(!state.current) return;
  const banner=$("#running-banner");
  banner.classList.add("show");
  $("#run-engine").disabled=true;
  await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  try{
    const raw=await pyCall("bridge.run_json(engine_id, preset_name, config_json)",{
      engine_id:state.current.id,
      preset_name:$("#preset-select").value,
      config_json:JSON.stringify(readControls())
    });
    const result=JSON.parse(raw);
    $("#kpi-grid").innerHTML=result.metrics.map(m=>`<div class="kpi"><span>${m.label}</span><strong>${fmt(m.value,m.format)}</strong></div>`).join("");
    plotChart("chart-1",result.charts[0]);
    plotChart("chart-2",result.charts[1]);
    $("#interpretation").textContent=result.summary;
    $("#model-note").textContent=result.note;
  }catch(err){
    console.error(err);
    $("#interpretation").textContent="The engine could not complete this scenario. Check the inputs and try again.";
    $("#model-note").textContent=String(err);
  }finally{
    banner.classList.remove("show");
    $("#run-engine").disabled=false;
  }
}

function mkdirp(path){
  const parts=path.split("/").filter(Boolean);
  let cur="";
  for(const p of parts){
    cur+="/"+p;
    try{state.pyodide.FS.mkdir(cur)}catch(e){}
  }
}

async function stageFile(src,dst){
  const res=await fetch(src);
  if(!res.ok) throw new Error("Could not load "+src);
  const text=await res.text();
  mkdirp(dst.split("/").slice(0,-1).join("/"));
  state.pyodide.FS.writeFile(dst,text,{encoding:"utf8"});
}

async function initPython(){
  const sourcePrefix = location.pathname.includes('/web/') ? '../' : '';
  try{
    setProgress(10,"Starting Python in the browser…");
    state.pyodide=await loadPyodide({indexURL:"https://cdn.jsdelivr.net/pyodide/v0.29.5/full/"});
    setProgress(30,"Loading scientific Python packages…");
    await state.pyodide.loadPackage(["numpy","pandas","scipy","pyyaml"]);

    const files=[
      ["bridge.py","/home/pyodide/bridge.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/__init__.py","/home/pyodide/engine01/risk_model/__init__.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/analysis.py","/home/pyodide/engine01/risk_model/analysis.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/frequency.py","/home/pyodide/engine01/risk_model/frequency.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/metrics.py","/home/pyodide/engine01/risk_model/metrics.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/mitigation.py","/home/pyodide/engine01/risk_model/mitigation.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/presets.py","/home/pyodide/engine01/risk_model/presets.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/schemas.py","/home/pyodide/engine01/risk_model/schemas.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/severity.py","/home/pyodide/engine01/risk_model/severity.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/simulation.py","/home/pyodide/engine01/risk_model/simulation.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/risk_model/stress.py","/home/pyodide/engine01/risk_model/stress.py"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/scenarios/individual_household.yaml","/home/pyodide/engine01/scenarios/individual_household.yaml"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/scenarios/solo_professional.yaml","/home/pyodide/engine01/scenarios/solo_professional.yaml"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/scenarios/small_business.yaml","/home/pyodide/engine01/scenarios/small_business.yaml"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/scenarios/saas_company.yaml","/home/pyodide/engine01/scenarios/saas_company.yaml"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/scenarios/mid_market.yaml","/home/pyodide/engine01/scenarios/mid_market.yaml"],
      [sourcePrefix+"engines/01-risk-exposure-loss-distribution/scenarios/enterprise.yaml","/home/pyodide/engine01/scenarios/enterprise.yaml"],
      [sourcePrefix+"engines/02-liquidity-cashflow-risk/engine.py","/home/pyodide/engine02.py"],
      [sourcePrefix+"engines/03-market-portfolio-risk/engine.py","/home/pyodide/engine03.py"],
      [sourcePrefix+"engines/04-credit-counterparty-risk/engine.py","/home/pyodide/engine04.py"],
      [sourcePrefix+"engines/05-monte-carlo-scenario-engine/engine.py","/home/pyodide/engine05.py"],
      [sourcePrefix+"engines/06-stress-reverse-stress/engine.py","/home/pyodide/engine06.py"],
      [sourcePrefix+"engines/07-risk-constrained-optimization/engine.py","/home/pyodide/engine07.py"],
      [sourcePrefix+"engines/08-integrated-risk-dependency/engine.py","/home/pyodide/engine08.py"]
    ];
    setProgress(55,"Connecting the eight risk engines…");
    let done=0;
    for(const [src,dst] of files){
      await stageFile(src,dst);
      done++;
      setProgress(55+Math.round(30*done/files.length),`Connecting engine components… ${done}/${files.length}`);
    }

    await state.pyodide.runPythonAsync("import sys; sys.path.insert(0, '/home/pyodide'); sys.path.insert(0, '/home/pyodide/engine01'); import bridge");
    setProgress(96,"Building the exploration workspace…");
    state.ready=true;
    await new Promise(r=>setTimeout(r,250));
    $("#boot").classList.add("hidden");
    setTimeout(()=>$("#boot").style.display="none",500);
  }catch(err){
    console.error(err);
    $("#boot-text").textContent="The browser runtime could not load. Refresh the page or check network access to the scientific package CDN.";
    $("#boot-progress").style.background="#ff6b6b";
  }
}

$("#preset-select").addEventListener("change",resetControls);
$("#reset-controls").addEventListener("click",resetControls);
$("#run-engine").addEventListener("click",runCurrent);

renderNavigation();
initPython();
