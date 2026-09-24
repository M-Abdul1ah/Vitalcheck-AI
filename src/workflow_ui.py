"""
Workflow tab: replays how the agents handled the most recent message.
Pure HTML/CSS/JS embedded via components.html, driven entirely by the
real trace recorded in app.py (see src/trace.py). No invented numbers.
"""
import json

import streamlit as st

NAMES = {
    "en": {"user": "User message", "safety": "Safety gate", "photo": "Photo prep",
           "retriever": "Retriever", "ai": "AI answer", "output": "Output check", "resolution": "Resolution"},
    "ur": {"user": "پیغام", "safety": "حفاظتی جانچ", "photo": "تصویر کی تیاری",
           "retriever": "تلاش", "ai": "AI جواب", "output": "آؤٹ پٹ جانچ", "resolution": "نتیجہ"},
}
SUB = {"user": "Text, photo", "safety": "Rules", "photo": "Pillow", "retriever": "Embeddings",
       "ai": "Llama 3.3", "output": "Rules", "resolution": "Outcome"}
MODEL = {"user": "Streamlit", "safety": "Rules", "photo": "Pillow",
         "retriever": "Multilingual MiniLM + ChromaDB", "ai": "Llama 3.3 70B on Groq",
         "output": "Rules", "resolution": "Orchestrator"}
EMPTY = {"en": "Send a message in the Chat tab. This tab will show exactly how the agents handled it.",
         "ur": "چیٹ ٹیب میں پیغام بھیجیں۔ یہ ٹیب دکھائے گا کہ ایجنٹس نے اسے کیسے سنبھالا۔"}
REPLAY = {"en": "Replay", "ur": "دوبارہ چلائیں"}
LEGEND = {"en": ["Waiting or skipped", "Running", "Done", "Warning", "Emergency"],
          "ur": ["منتظر یا نظرانداز", "جاری", "مکمل", "انتباہ", "ایمرجنسی"]}

TEMPLATE = r"""
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#16302B">
<style>
:root{--ink:#16302B;--muted:#5B6F6A;--brand:#0B4F4A;--line:#D5E0DC;--surf:#F5F7F6}
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600&display=swap');
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.rtl #wflog,.rtl #wfinsp,.rtl .lg,.rtl .lb,.rtl .empty,.rtl #wfclk{direction:rtl;text-align:right;font-family:'Noto Nastaliq Urdu',serif;line-height:1.9}
.run>rect{animation:pulse .9s ease-in-out infinite}
.node rect{fill:#fff;stroke:var(--line)}
.node text{fill:var(--ink);font-size:12px}
.node .sub{fill:var(--muted);font-size:10px}
.blue rect{stroke:#378ADD;stroke-width:2}
.teal rect{stroke:#1D9E75;stroke-width:2;fill:#EAF7F1}
.amber rect{stroke:#BA7517;stroke-width:2;fill:#FFF6E7}
.red rect{stroke:#E24B4A;stroke-width:2;fill:#FDECEC}
.gray rect{stroke:var(--line)}
.node{cursor:pointer}
.arr{stroke:#B9C7C2;stroke-width:1.5}
button.wf{font-size:13px;padding:6px 14px;border-radius:8px;border:1px solid var(--line);background:#fff;cursor:pointer}
button.wf:hover{border-color:var(--brand);color:var(--brand)}
.lg{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:var(--muted);margin-right:12px}
.lg i{display:inline-block;width:9px;height:9px;border-radius:2px}
#wflog div{padding:2px 0;font-size:12px;line-height:1.5}
.mb{display:flex;align-items:center;gap:8px;font-size:12px;margin:5px 0}
.mt{flex:1;height:6px;border-radius:3px;background:#E3EFEC}
.mf{display:block;height:6px;border-radius:3px;background:var(--brand)}
.lb{font-size:11px;color:var(--muted);margin:8px 0 2px}
.sg{height:22px;line-height:22px;padding:0 5px;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.empty{padding:32px 16px;text-align:center;color:var(--muted);font-size:13px}
</style>
__BODY__
<script>
var NAMES=__NAMES__, SUB=__SUB__, MODEL=__MODEL__, TRACE=__TRACE__, LBL=__LBL__, RTL=__RTL__;
var E={"user-safety":[160,58,198,58],"safety-photo":[320,58,358,58],"photo-retriever":[480,58,518,58],
"retriever-ai":[580,86,580,168],"ai-output":[520,198,482,198],"output-resolution":[360,198,322,198],
"safety-resolution":[260,86,260,168]};
var CLS={idle:"node gray",run:"node blue run",done:"node teal",warn:"node amber",alert:"node red",skip:"node gray"};
var SEG={done:["#9FE1CB","#085041"],warn:["#FAC775","#633806"],alert:["#F7C1C1","#791F1F"]};
if(RTL){document.getElementById("wfroot").classList.add("rtl")}
if(!TRACE){document.getElementById("wfroot").innerHTML='<div class="empty">'+LBL.empty+'</div>';}
else{
var dot=document.getElementById("dot"),logEl=document.getElementById("wflog"),resEl=document.getElementById("wfres"),
    inspEl=document.getElementById("wfinsp"),strip=document.getElementById("wfstrip"),clk=document.getElementById("wfclk");
var run=0,pinned=null,DATA={},reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
function fmt(ms){return ms>=1000?(ms/1000).toFixed(1)+" s":ms+" ms"}
function setState(id,s){var g=document.getElementById("n-"+id);if(!g)return;g.setAttribute("class",CLS[s]);g.querySelector("rect").style.strokeDasharray=(s==="skip")?"4 3":""}
function setSub(id,tx){var e=document.querySelector("#n-"+id+" .sub");if(e)e.textContent=tx}
function block(l,tx){return "<div class=\"lb\">"+l+"</div><div style=\"line-height:1.5;word-break:break-word\">"+tx+"</div>"}
function insp(id){
  var d=DATA[id];
  if(!d){inspEl.innerHTML="<div style=\"color:var(--muted)\">"+NAMES[id]+"</div>";return}
  var h="<div style=\"display:flex;justify-content:space-between;gap:8px;align-items:baseline\"><span style=\"font-weight:600\">"+NAMES[id]+"</span><span style=\"font-size:11px;color:var(--muted);text-align:right\">"+MODEL[id]+(d.ms?" · "+fmt(d.ms):"")+"</span></div>";
  h+=block(LBL.received,d.inn||"-");
  if(d.matches){h+="<div class=\"lb\">"+LBL.returned+"</div>";d.matches.forEach(function(m){h+="<div class=\"mb\"><span style=\"min-width:110px\">"+m[0]+"</span><span class=\"mt\"><span class=\"mf\" style=\"width:"+Math.round(m[1]*100)+"%\"></span></span><span style=\"min-width:32px;text-align:right\">"+m[1].toFixed(2)+"</span></div>"})}
  else if(d.stream){h+="<div class=\"lb\">"+LBL.returned+"</div><div style=\"white-space:pre-wrap;line-height:1.5\">"+d.stream+"</div>"}
  else{h+=block(LBL.returned,d.out||"-")}
  inspEl.innerHTML=h;
}
function reset(){
  Object.keys(NAMES).forEach(function(k){setState(k,"idle");setSub(k,SUB[k])});
  logEl.innerHTML="";strip.innerHTML="";resEl.style.display="none";DATA={};
  dot.setAttribute("cx",-20);dot.setAttribute("cy",-20);clk.textContent=LBL.elapsed+" 0 ms";
  inspEl.innerHTML="<div style=\"color:var(--muted)\">"+LBL.hint+"</div>";
}
function moveDot(k,ms,color,me){return new Promise(function(done){var p=E[k];if(!p){done();return}var t0=performance.now(),d=reduce?ms/4:ms;dot.setAttribute("fill",color);(function f(t){var q=Math.min(1,(t-t0)/d);dot.setAttribute("cx",p[0]+(p[2]-p[0])*q);dot.setAttribute("cy",p[1]+(p[3]-p[1])*q);if(q<1&&me===run){requestAnimationFrame(f)}else{dot.setAttribute("cx",-20);dot.setAttribute("cy",-20);done()}})(t0)})}
function sleep(ms){return new Promise(function(r){setTimeout(r,reduce?ms/4:ms)})}
async function play(){
  var me=++run,steps=TRACE.steps;reset();
  var total=steps.reduce(function(a,s){return a+(s.ms||0)},0)||1,cum=0;
  for(var i=0;i<steps.length;i++){
    var st=steps[i];
    if(st.skip){st.skip.forEach(function(id){setState(id,"skip");setSub(id,LBL.skipped)});var d0=document.createElement("div");d0.style.color="var(--muted)";d0.textContent=st.log;logEl.appendChild(d0);continue}
    var id=st.id,ms=st.ms||0;
    var d={inn:st.inn,out:st.out,matches:st.matches,stream:null,ms:ms};
    DATA[id]=d;setState(id,"run");if(!pinned)insp(id);
    if(st.stream){
      var words=st.stream.split(/(\s+)/);d.stream="";
      for(var w=0;w<words.length;w++){d.stream+=words[w];if(!pinned||pinned===id)insp(id);await sleep(words[w].trim()?22:0);if(me!==run)return}
    } else { await sleep(id==="retriever"?500:350); if(me!==run) return }
    cum+=ms;
    setState(id,st.st);setSub(id,st.sub||fmt(ms));
    clk.textContent=LBL.elapsed+" "+cum.toLocaleString()+" ms";
    var row=document.createElement("div");row.innerHTML="<span style=\"display:inline-block;min-width:58px;color:var(--muted)\">+"+cum.toLocaleString()+" ms</span><span style=\"color:var(--muted)\">"+NAMES[id]+"</span> · "+st.log;logEl.appendChild(row);
    if(ms>0){var sg=document.createElement("div"),c=SEG[st.st]||SEG.done;sg.className="sg";sg.style.width=Math.max(4,ms/total*100)+"%";sg.style.background=c[0];sg.style.color=c[1];sg.textContent=NAMES[id]+" "+fmt(ms);sg.title=sg.textContent;strip.appendChild(sg)}
    if(!pinned||pinned===id)insp(id);
    if(st.edge){await moveDot(st.edge,320,st.st==="alert"?"#E24B4A":"#378ADD",me);if(me!==run)return}
  }
  clk.textContent=LBL.total+" "+cum.toLocaleString()+" ms";
  var tone=TRACE.tone,c2=tone==="success"?["#EAF7F1","#0B4F4A"]:tone==="danger"?["#FDECEC","#791F1F"]:["#FFF6E7","#633806"];
  resEl.style.background=c2[0];resEl.style.color=c2[1];resEl.textContent=TRACE.end;resEl.style.display="block";
}
Object.keys(NAMES).forEach(function(id){var g=document.getElementById("n-"+id);if(g)g.addEventListener("click",function(){pinned=id;insp(id)})});
document.getElementById("wfreplay").addEventListener("click",play);
play();
}
</script>
</div>
"""

DIAGRAM = """
<div id="wfroot">
<div style="display:flex;justify-content:space-between;align-items:center;margin:0 0 8px">
  <span style="font-size:12px;color:var(--muted)" id="wfclk">Elapsed 0 ms</span>
  <button class="wf" id="wfreplay">__REPLAY__</button>
</div>
<svg width="100%" viewBox="0 0 680 270" role="img" style="max-width:640px">
<title>Agent workflow</title>
<defs><marker id="wfarrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#B9C7C2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
<line x1="160" y1="58" x2="198" y2="58" class="arr" marker-end="url(#wfarrow)"/>
<line x1="320" y1="58" x2="358" y2="58" class="arr" marker-end="url(#wfarrow)"/>
<line x1="480" y1="58" x2="518" y2="58" class="arr" marker-end="url(#wfarrow)"/>
<line x1="580" y1="86" x2="580" y2="168" class="arr" marker-end="url(#wfarrow)"/>
<line x1="520" y1="198" x2="482" y2="198" class="arr" marker-end="url(#wfarrow)"/>
<line x1="360" y1="198" x2="322" y2="198" class="arr" marker-end="url(#wfarrow)"/>
<line x1="260" y1="86" x2="260" y2="168" class="arr" stroke-dasharray="4 3" marker-end="url(#wfarrow)"/>
<g id="n-user" class="node gray"><rect x="40" y="30" width="120" height="56" rx="8"/><text x="100" y="49" text-anchor="middle" dominant-baseline="central">__N_user__</text><text class="sub" x="100" y="67" text-anchor="middle" dominant-baseline="central"></text></g>
<g id="n-safety" class="node gray"><rect x="200" y="30" width="120" height="56" rx="8"/><text x="260" y="49" text-anchor="middle" dominant-baseline="central">__N_safety__</text><text class="sub" x="260" y="67" text-anchor="middle" dominant-baseline="central"></text></g>
<g id="n-photo" class="node gray"><rect x="360" y="30" width="120" height="56" rx="8"/><text x="420" y="49" text-anchor="middle" dominant-baseline="central">__N_photo__</text><text class="sub" x="420" y="67" text-anchor="middle" dominant-baseline="central"></text></g>
<g id="n-retriever" class="node gray"><rect x="520" y="30" width="120" height="56" rx="8"/><text x="580" y="49" text-anchor="middle" dominant-baseline="central">__N_retriever__</text><text class="sub" x="580" y="67" text-anchor="middle" dominant-baseline="central"></text></g>
<g id="n-ai" class="node gray"><rect x="520" y="170" width="120" height="56" rx="8"/><text x="580" y="189" text-anchor="middle" dominant-baseline="central">__N_ai__</text><text class="sub" x="580" y="207" text-anchor="middle" dominant-baseline="central"></text></g>
<g id="n-output" class="node gray"><rect x="360" y="170" width="120" height="56" rx="8"/><text x="420" y="189" text-anchor="middle" dominant-baseline="central">__N_output__</text><text class="sub" x="420" y="207" text-anchor="middle" dominant-baseline="central"></text></g>
<g id="n-resolution" class="node gray"><rect x="200" y="170" width="120" height="56" rx="8"/><text x="260" y="189" text-anchor="middle" dominant-baseline="central">__N_resolution__</text><text class="sub" x="260" y="207" text-anchor="middle" dominant-baseline="central"></text></g>
<circle id="dot" r="6" cx="-20" cy="-20" fill="#378ADD"/>
</svg>
<div id="wfstrip" style="display:flex;gap:2px;height:22px;background:var(--surf);border-radius:8px;overflow:hidden;margin:4px 0 8px"></div>
<div style="margin:0 0 10px">__LEGEND__</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:10px">
<div id="wflog" style="min-width:0;background:var(--surf);border-radius:10px;padding:8px 14px;font-size:12px;min-height:200px"></div>
<div id="wfinsp" style="min-width:0;background:var(--surf);border-radius:10px;padding:8px 14px;font-size:12px;min-height:200px"></div>
</div>
<div id="wfres" style="display:none;margin-top:10px;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:500"></div>
</div>
"""


def render_trace(trace: dict | None, lang: str = "en", height: int = 640) -> None:
    lang = lang if lang in NAMES else "en"
    colors = ["#888780", "#378ADD", "#1D9E75", "#BA7517", "#E24B4A"]
    legend = "".join(
        f'<span class="lg"><i style="background:{c}"></i>{name}</span>'
        for c, name in zip(colors, LEGEND[lang])
    )
    body = DIAGRAM.replace("__REPLAY__", REPLAY[lang]).replace("__LEGEND__", legend)
    for k, v in NAMES[lang].items():
        body = body.replace(f"__N_{k}__", v)

    labels = {
        "empty": EMPTY[lang], "received": "Received" if lang == "en" else "موصول",
        "returned": "Returned" if lang == "en" else "نتیجہ",
        "hint": ("Click a box to inspect what it received and returned."
                 if lang == "en" else "کسی بھی خانے پر کلک کریں۔"),
        "elapsed": "Elapsed" if lang == "en" else "وقت",
        "total": "Total" if lang == "en" else "کل",
        "skipped": "skipped" if lang == "en" else "نظرانداز",
    }
    html = (
        TEMPLATE.replace("__BODY__", body)
        .replace("__NAMES__", json.dumps(NAMES[lang]))
        .replace("__SUB__", json.dumps(SUB))
        .replace("__MODEL__", json.dumps(MODEL))
        .replace("__TRACE__", json.dumps(trace) if trace else "null")
        .replace("__LBL__", json.dumps(labels))
        .replace("__RTL__", "true" if lang == "ur" else "false")
    )
    st.iframe(html, height=height)
