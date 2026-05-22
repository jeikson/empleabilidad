#!/usr/bin/env python3
"""Build Empleabilidad 1 — con contenido detallado extraído de PDFs."""

import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "index.html"
DOCS_DIR = ROOT / "assets" / "docs" / "parte-1"
TEXTS_DIR = ROOT / "build" / "texts" / "parte-1"
CUESTIONARIO = ROOT / "source" / "parte-1-cuestionario.json"

# Map unit IDs to their main PDF key for text extraction
UNIT_PDFS = {
    "U1": "U1_Empleo_y_competencias_profesionales_actuales---269ec1c5-9eb0-4a5f-bc53-b94d24ec3eb4",
    "U2": "U2_Evaluación_de_riesgos_profesionales---f5e2a5a9-a541-4029-8361-5f6af43a4d98",
    "U3": "U3_Medidas_de_prevención_y_protección_en_la_empresa---4ddcd711-c693-4693-ab4b-c730f3619fbc",
    "U4": "U4_Condiciones_laborales_I---c55c38d3-faec-46ed-b5bf-7bd9ec3afa03",
    "U5": "U5_Condiciones_laborales_II---933daac0-a694-46c6-a61a-86d78a7d1594",
    "U6": "U6_Condiciones_laborales_III---53fe7c19-afc1-4c38-b336-6fb69c1ddf4c",
    "U7": "U7_Seguridad_Social---3f38eb20-042f-4727-b8b5-74a0e4624e8d",
    "U8": "U8_Potencial_profesional_y_auto-orientación_laboral---db009e1f-8c1a-411b-8dfd-3c1d16da281d",
    "U9": "U9_Aprendizaje_autónomo_y_herramientas_digitales---e8725de7-fe88-44e8-aac3-3092264e38d0",
}

UNITS = [
    {"id":"U1","emoji":"\U0001f4bc","title":"Empleo y competencias profesionales actuales",
     "topics":["Opciones profesionales","Empleadores p\u00fablicos y privados","Acceso al empleo p\u00fablico","Oportunidades de aprendizaje en Europa","Competencias profesionales"]},
    {"id":"U2","emoji":"\u26a0\ufe0f","title":"Evaluaci\u00f3n de riesgos profesionales",
     "topics":["Conceptos b\u00e1sicos de riesgos","Factores de riesgo en el trabajo","Evaluaci\u00f3n y prevenci\u00f3n","Da\u00f1os derivados del trabajo"]},
    {"id":"U3","emoji":"\U0001f6e1\ufe0f","title":"Medidas de prevenci\u00f3n y protecci\u00f3n en la empresa",
     "topics":["Principios de la actividad preventiva","Protecci\u00f3n colectiva e individual","EPIs","Organizaci\u00f3n de la prevenci\u00f3n"]},
    {"id":"U4","emoji":"\U0001f4cb","title":"Condiciones laborales I",
     "topics":["Jornada laboral y l\u00edmites","Descanso semanal y vacaciones","Salario y modalidades","Delegados y garant\u00edas"]},
    {"id":"U5","emoji":"\u2696\ufe0f","title":"Condiciones laborales II",
     "topics":["Contrato de trabajo","Derechos y deberes","Jerarqu\u00eda normativa","Modificaci\u00f3n y suspensi\u00f3n"]},
    {"id":"U6","emoji":"\U0001f50d","title":"Condiciones laborales III",
     "topics":["Despido disciplinario y objetivo","Extinci\u00f3n del contrato","Indemnizaciones","FOGASA"]},
    {"id":"U7","emoji":"\U0001f3e5","title":"Seguridad Social",
     "topics":["Estructura del sistema","Reg\u00edmenes de la SS","Prestaciones","Afiliaci\u00f3n y cotizaci\u00f3n"]},
    {"id":"U8","emoji":"\U0001f9ed","title":"Potencial profesional y auto-orientaci\u00f3n laboral",
     "topics":["Autoconocimiento","Intereses profesionales y test de Holland","Habilidades duras y blandas","Plan de carrera"]},
    {"id":"U9","emoji":"\U0001f4da","title":"Aprendizaje aut\u00f3nomo y herramientas digitales",
     "topics":["Estrategias de aprendizaje","Herramientas digitales","Formaci\u00f3n continua","Certificaciones"]},
]

CSS = """
:root{--bg:#0a0f1f;--card:#111827;--card2:#1a2332;--a:#00d4aa;--a2:#7c5bf0;--t:#e8ecf5;--t2:#8892b0;--b:#4a9eff;--y:#f5c842;--o:#ff9f43}
*{margin:0;padding:0;box-sizing:border-box;scroll-behavior:smooth}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--t);min-height:100vh}::selection{background:rgba(0,212,170,.25)}
.topbar{background:linear-gradient(135deg,#0a1025,#14203a);padding:12px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.06);position:sticky;top:0;z-index:100;flex-wrap:wrap;gap:8px}
.topbar h1{font-size:17px;font-weight:800;background:linear-gradient(135deg,var(--a),#48dbfb);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.topbar .sub{font-size:10px;color:var(--t2);-webkit-text-fill-color:var(--t2)}
.searchbox{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:8px 12px;color:var(--t);width:200px;font-size:12px;outline:none;transition:.3s}
.searchbox:focus{border-color:var(--a);background:rgba(0,212,170,.05);width:240px}.searchbox::placeholder{color:var(--t2);opacity:.6}
.nav{display:flex;gap:5px;padding:10px 20px;background:rgba(10,14,26,.95);border-bottom:1px solid rgba(255,255,255,.04);position:sticky;top:47px;z-index:99;overflow-x:auto}
.nav-btn{padding:6px 14px;border-radius:8px;border:none;cursor:pointer;font-weight:600;font-size:11px;transition:.2s;background:var(--card);color:var(--t2);white-space:nowrap;flex-shrink:0}
.nav-btn:hover{background:var(--card2);transform:translateY(-1px)}
.nav-btn.active{background:linear-gradient(135deg,var(--a),#00b894);color:#0a0e1a;box-shadow:0 2px 12px rgba(0,212,170,.2)}
.main{max-width:1000px;margin:0 auto;padding:14px 18px 50px}
.unit{display:none;animation:fadeIn .3s}.unit.active{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.hero{background:linear-gradient(135deg,var(--card),#0e1729);border-radius:12px;padding:20px 24px;margin-bottom:14px;border:1px solid rgba(255,255,255,.05)}
.hero h2{font-size:18px;font-weight:700;margin-bottom:5px}.hero h2 .c{color:var(--a)}.hero p{color:var(--t2);font-size:12px}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.badge{padding:3px 9px;border-radius:5px;font-size:10px;font-weight:500}
.b1{background:rgba(0,212,170,.12);color:var(--a)}.b2{background:rgba(74,158,255,.12);color:var(--b)}.b3{background:rgba(124,91,240,.12);color:var(--a2)}
.secc{background:var(--card);border-radius:12px;margin-bottom:10px;border:1px solid rgba(255,255,255,.04);overflow:hidden}
.sech{display:flex;align-items:center;gap:8px;padding:12px 16px;cursor:pointer;user-select:none;transition:.15s;font-size:13px;font-weight:600}
.sech:hover{background:rgba(255,255,255,.02)}
.sech .arrow{font-size:10px;transition:.2s;width:16px;text-align:center;color:var(--a);flex-shrink:0}
.sech .arrow.o{transform:rotate(90deg)}
.sech .num{color:var(--a);font-weight:700;min-width:30px;font-size:12px}
.secb{display:none;padding:0 16px 14px;border-top:1px solid rgba(255,255,255,.04);padding-top:10px}
.secb.open{display:block}
.stitle{padding:6px 10px;font-size:12px;font-weight:600;color:var(--t);background:var(--card2);border-radius:6px;margin:8px 0 6px;display:flex;align-items:center;gap:6px;border-left:3px solid var(--a)}
.stitle.purple{border-left-color:var(--a2)}.stitle.orange{border-left-color:var(--o)}
.cbody{padding:2px 6px}.cbody p{font-size:12px;line-height:1.65;color:var(--t2);margin-bottom:8px}.cbody p strong{color:var(--t)}
.cbody ul{list-style:none;padding:0 4px}.cbody ul li{font-size:12px;color:var(--t2);padding:3px 0 3px 18px;position:relative;line-height:1.5}
.cbody ul li::before{content:"\\25B8";position:absolute;left:2px;color:var(--a);font-weight:700}
.tbl{overflow-x:auto;margin:6px 0;border-radius:6px;font-size:11px}
.tbl table{width:100%;border-collapse:collapse}
.tbl th{background:var(--card2);color:var(--a);padding:6px 10px;text-align:left;font-weight:600;border-bottom:1px solid rgba(0,212,170,.15);white-space:nowrap;font-size:11px}
.tbl td{padding:5px 10px;border-bottom:1px solid rgba(255,255,255,.04);color:var(--t2);vertical-align:top}
.tbl tr:hover td{background:rgba(0,212,170,.03)}
a{color:var(--a);text-decoration:none}a:hover{text-decoration:underline}
.st{position:fixed;bottom:20px;right:20px;width:36px;height:36px;border-radius:50%;background:var(--a);color:#0a0e1a;border:none;cursor:pointer;font-size:18px;opacity:0;transition:.3s;pointer-events:none;z-index:50;box-shadow:0 3px 12px rgba(0,212,170,.3)}
.st.v{opacity:1;pointer-events:auto}
@media(max-width:768px){
  .topbar{padding:10px 14px}.searchbox{width:100%;margin-top:6px}.searchbox:focus{width:100%}
  .nav{top:92px;padding:8px 12px}.main{padding:10px 12px}.hero{padding:14px 16px}.hero h2{font-size:15px}
  .sech{padding:10px 12px;font-size:12px}
}
"""

def esc(t): return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;").replace("'","&#39;")

def clean_title(name):
    c = re.sub(r"---[a-f0-9-]+","",name)
    c = c.replace("DIAPOSITIVAS_","Diapositivas: ").replace("_Síntesis_"," (Síntesis) ").replace("_Síntesis._"," (Síntesis) ").replace("_"," ").strip()
    return re.sub(r"\s+"," ",c)

def load_pdfs():
    by_u={}
    if not DOCS_DIR.exists(): return by_u
    for f in sorted(DOCS_DIR.iterdir()):
        if f.suffix.lower()!=".pdf": continue
        n=f.stem;kb=f.stat().st_size/1024;sz=f"{kb/1024:.1f}MB" if kb>1024 else f"{kb:.0f}KB"
        m=re.match(r"(U\d+)",n);k=m.group(1) if m else "ZZ"
        by_u.setdefault(k,[]).append({"title":clean_title(n),"file":f"assets/docs/parte-1/{f.name}","size":sz})
    return by_u

def load_q(): return json.loads(CUESTIONARIO.read_text("utf-8")) if CUESTIONARIO.exists() else []

def extract_sections(pdf_key):
    txt_path = TEXTS_DIR / f"{pdf_key}.txt"
    if not txt_path.exists(): return [], ""
    text = txt_path.read_text("utf-8", errors="replace")
    intro = ""
    m_intro = re.search(r"(?:Introducción|Introducci[óo]n)(.*?)(?=\n\s*(?:\d+\.\d+|\d+\.)\s)", text, re.DOTALL)
    if m_intro:
        intro = m_intro.group(1).strip()
        intro = re.sub(r"[^\S\n]{3,}"," ",intro)
        intro = re.sub(r"\n{2,}","\n\n",intro)
    sections = []
    pattern = r"(\d+\.\d+(?:\.\d+)?)\.?\s*\n\s*([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ\s,;:()]+?)(?=\n)"
    matches = list(re.finditer(pattern, text))
    for i,m in enumerate(matches):
        num=m.group(1);title=m.group(2).strip()
        start=m.end();end=matches[i+1].start() if i+1<len(matches) else len(text)
        content=text[start:end].strip()
        content=re.sub(r"[^\S\n]{3,}"," ",content)
        content=re.sub(r"\n{2,}","\n\n",content)
        if len(content)>2000:content=content[:2000]+"..."
        if len(title)>5 and len(title)<120:sections.append({"num":num,"title":title,"content":content})
    return sections, intro

def build():
    pdfs=load_pdfs();qs=load_q()
    parts=[]
    parts.append(f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Empleabilidad 1 — Gu&iacute;a Detallada</title><style>{CSS}</style></head><body>
<div class="topbar"><div><h1>\U0001f4cb Empleabilidad 1</h1><div class="sub">Gu&iacute;a interactiva detallada &bull; {len(UNITS)} unidades &bull; {len(qs)} preguntas</div></div><input class="searchbox" id="s" placeholder="\U0001f50d Buscar..." oninput="su(this.value)"></div>
<div class="nav" id="nav">''')
    for i,u in enumerate(UNITS):
        a=" active" if i==0 else ""
        parts.append(f'<button class="nav-btn{a}" onclick="x({i})"><b>{u["id"]}</b> {esc(u["title"][:28])}&hellip;</button>')
    parts.append(f'<button class="nav-btn" onclick="x({len(UNITS)})"><b>\U0001f4dd</b> Cuestionario</button>')
    parts.append(f'<button class="nav-btn" onclick="x({len(UNITS)+1})"><b>\U0001f4da</b> Documentos</button>')
    parts.append('</div><div class="main" id="m">')

    for i,u in enumerate(UNITS):
        a=" active" if i==0 else ""
        d=pdfs.get(u["id"],[])
        uid=u["id"]
        pdf_key=UNIT_PDFS.get(uid,"")
        sections, intro = extract_sections(pdf_key) if pdf_key else ([],"")
        
        parts.append(f'''<div class="unit{a}" id="u{i}"><div class="hero"><h2>{u["emoji"]} <span class="c">{uid}:</span> {esc(u["title"])}</h2><p>{esc(", ".join(u["topics"]))}</p><div class="badges"><span class="badge b1">\U0001f4d6 {len(u["topics"])} temas</span><span class="badge b2">\U0001f4c4 {len(d)} documentos</span><span class="badge b3">{len(sections)} secciones</span></div></div>''')

        # Introduction
        if intro:
            intro_p=" ".join(intro.split()[:120])
            parts.append(f'<div class="secc"><div class="sech" onclick="t(this)"><span class="arrow">\u25b6</span><span class="num">\U0001f4d6</span>Introducci&oacute;n</div><div class="secb"><div class="cbody"><p>{esc(intro_p)}</p></div></div></div>')

        # Detailed sections
        for s in sections[:8]:
            cp=s["content"].replace("\n\n","</p><p>").replace("\n"," ")
            parts.append(f'<div class="secc"><div class="sech" onclick="t(this)"><span class="arrow">\u25b6</span><span class="num">{s["num"]}</span>{esc(s["title"][:70])}</div><div class="secb"><div class="cbody"><p>{esc(cp[:2500])}</p></div></div></div>')

        # Topics
        parts.append(f'<div class="secc"><div class="sech" onclick="t(this)"><span class="arrow">\u25b6</span><span class="num">{uid}</span>Temas principales</div><div class="secb"><div class="stitle purple">\U0001f4cc Contenido</div><div class="cbody"><ul>')
        for t in u["topics"]: parts.append(f"<li>{esc(t)}</li>")
        parts.append("</ul></div></div></div>")

        # Docs
        if d:
            r="".join(f'<tr><td>{esc(x["title"][:70])}</td><td>{x["size"]}</td><td><a href="{esc(x["file"])}" target="_blank" rel="noopener">PDF \U0001f4c4</a></td></tr>' for x in d)
            parts.append(f'<div class="secc"><div class="sech" onclick="t(this)"><span class="arrow">\u25b6</span><span class="num">\U0001f4ce</span>Documentos fuente</div><div class="secb"><div class="tbl"><table><tr><th>Documento</th><th>Tama\u00f1o</th><th>Abrir</th></tr>{r}</table></div></div></div>')
        parts.append("</div>")

    # Quiz
    ql=len(UNITS)
    parts.append(f'''<div class="unit" id="u{ql}"><div class="hero"><h2>\U0001f4dd <span class="c">Cuestionario</span> de repaso</h2><p>{len(qs)} preguntas con solo la respuesta correcta</p><div class="badges"><span class="badge b1">\U0001f4dd {len(qs)} preguntas</span><span class="badge b3">\U0001f4dd Quiz</span></div></div>''')
    for g in range(0,len(qs),10):
        gn=g//10+1;s=g+1;e=min(g+10,len(qs))
        r="".join(f'<tr><td>{esc(q["pregunta"])}</td><td>{esc(q["respuesta_correcta"])}</td></tr>' for q in qs[g:min(g+10,len(qs))])
        parts.append(f'<div class="secc"><div class="sech" onclick="t(this)"><span class="arrow">\u25b6</span><span class="num">Q.{gn}</span>Preguntas {s}-{e}</div><div class="secb"><div class="stitle purple">\U0001f4ca Cuestionario</div><div class="cbody"><div class="tbl"><table><tr><th>Pregunta</th><th>Respuesta correcta</th></tr>{r}</table></div></div></div></div>''')
    parts.append("</div>")

    # Doc library
    dl=len(UNITS)+1
    parts.append(f'''<div class="unit" id="u{dl}"><div class="hero"><h2>\U0001f4da <span class="c">Biblioteca</span> de documentos</h2><p>Todos los PDFs</p></div><div class="lib-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px">''')
    for uk in sorted(pdfs.keys()):
        for x in pdfs[uk]:
            parts.append(f'<a class="doc-link" style="display:flex;flex-direction:column;gap:4px;padding:12px 14px;background:var(--card);border-radius:10px;border:1px solid rgba(255,255,255,.04);text-decoration:none" href="{esc(x["file"])}" target="_blank" rel="noopener"><span style="font-size:12px;font-weight:600;color:var(--t)">{esc(x["title"][:60])}</span><span style="font-size:10px;color:var(--t2)">{x["size"]}</span></a>')
    parts.append("</div></div></div>")

    parts.append('''<button class="st" id="st" onclick="window.scrollTo({top:0,behavior:'smooth'})">&uarr;</button>
<script>
let ui=0;
function x(i){
  let u=document.getElementById('u'+i),b=document.querySelectorAll('.nav-btn');
  let p=document.getElementById('u'+ui);if(p)p.classList.remove('active');
  if(b[ui])b[ui].classList.remove('active');
  ui=i;if(u)u.classList.add('active');
  if(b[i]){b[i].classList.add('active');b[i].scrollIntoView({behavior:'smooth',inline:'center',block:'nearest'})}
  window.scrollTo({top:0,behavior:'smooth'})
}
function t(el){
  const b=el.nextElementSibling,a=el.querySelector('.arrow');
  if(b&&b.classList.contains('secb')){b.classList.toggle('open');if(a)a.classList.toggle('o')}
}
function su(v){
  const q=v.toLowerCase();
  document.querySelectorAll('.secc').forEach(s=>{s.style.display=s.textContent.toLowerCase().includes(q)?'':'none'})
}
window.addEventListener('scroll',()=>{const s=document.getElementById('st');if(window.scrollY>300)s.classList.add('v');else s.classList.remove('v')});
</script></body></html>''')

    OUT.write_text("\n".join(parts),"utf-8")
    dcount=sum(len(v) for v in pdfs.values())
    print(f"\u2705 Generated Empleabilidad 1 ({OUT})")
    print(f"   \u2022 {len(UNITS)} unidades con contenido extra\u00eddo de PDFs")
    print(f"   \u2022 {dcount} documentos")
    print(f"   \u2022 {len(qs)} quiz questions")

if __name__=="__main__": build()
