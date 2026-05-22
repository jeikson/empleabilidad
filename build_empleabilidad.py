#!/usr/bin/env python3
"""Build the Empleabilidad interactive study guide."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "index.html"
ASSETS_DOCS = ROOT / "assets" / "docs" / "parte-1"
CUESTIONARIO = ROOT / "source" / "parte-1-cuestionario.json"

UNITS = [
    {"id": "U1", "emoji": "\U0001f4bc", "title": "Empleo y competencias profesionales actuales",
     "topics": ["Mercado laboral: oferta, demanda e intermediarios", "Relaciones laborales y tipos de contratos",
                "Economía gig y nuevas formas de trabajo", "Competencias profesionales y habilidades"]},
    {"id": "U2", "emoji": "\u26a0\ufe0f", "title": "Evaluación de riesgos profesionales",
     "topics": ["Conceptos básicos de riesgos laborales", "Factores de riesgo en el entorno laboral",
                "Evaluación y prevención de riesgos", "Daños derivados del trabajo"]},
    {"id": "U3", "emoji": "\U0001f6e1\ufe0f", "title": "Medidas de prevención y protección en la empresa",
     "topics": ["Principios de la actividad preventiva", "Medidas de protección colectiva e individual",
                "Equipos de protección individual (EPI)", "Organización de la prevención en la empresa"]},
    {"id": "U4", "emoji": "\U0001f4cb", "title": "Condiciones laborales I",
     "topics": ["La jornada laboral y sus límites", "Descanso semanal y vacaciones",
                "El salario y sus modalidades", "Delegados y garantías laborales"]},
    {"id": "U5", "emoji": "\u2696\ufe0f", "title": "Condiciones laborales II",
     "topics": ["El contrato de trabajo y sus tipos", "Derechos y deberes del trabajador",
                "Jerarquía normativa y principios de interpretación", "Modificaciones y suspensión del contrato"]},
    {"id": "U6", "emoji": "\U0001f50d", "title": "Condiciones laborales III",
     "topics": ["Despido disciplinario y despido objetivo", "Extinción del contrato de trabajo",
                "Indemnizaciones y finiquito", "El FOGASA y su función"]},
    {"id": "U7", "emoji": "\U0001f3e5", "title": "Seguridad Social",
     "topics": ["Estructura del sistema de Seguridad Social", "Regímenes: general y especiales",
                "Prestaciones contributivas y no contributivas", "Afiliación, altas y bajas"]},
    {"id": "U8", "emoji": "\U0001f9ed", "title": "Potencial profesional y auto-orientación laboral",
     "topics": ["Autoconocimiento y perfil profesional", "Intereses profesionales y test de Holland",
                "Habilidades duras y blandas", "Proyecto profesional y plan de carrera"]},
    {"id": "U9", "emoji": "\U0001f4da", "title": "Aprendizaje autónomo y herramientas digitales",
     "topics": ["Estrategias de aprendizaje autónomo", "Herramientas digitales para el estudio",
                "Formación continua y reciclaje profesional", "Alternativas de formación y certificaciones"]},
]


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")


def clean_pdf_title(name: str) -> str:
    cleaned = re.sub(r"---[a-f0-9-]+", "", name)
    cleaned = cleaned.replace("DIAPOSITIVAS_", "Diapositivas: ")
    cleaned = cleaned.replace("_Síntesis_", " (Síntesis) ")
    cleaned = cleaned.replace("_", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def load_pdfs():
    by_unit = {}
    if not ASSETS_DOCS.exists():
        return by_unit
    for f in sorted(ASSETS_DOCS.iterdir()):
        if f.suffix.lower() != ".pdf":
            continue
        name = f.stem
        size_kb = f.stat().st_size / 1024
        size_str = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
        m = re.match(r"(U\d+)", name)
        unit_key = m.group(1) if m else "ZZ"
        by_unit.setdefault(unit_key, []).append({
            "title": clean_pdf_title(name),
            "file": f"assets/docs/parte-1/{f.name}",
            "size": size_str,
        })
    return by_unit


def load_quiz():
    if not CUESTIONARIO.exists():
        return []
    return json.loads(CUESTIONARIO.read_text(encoding="utf-8"))


def build():
    pdfs_by_unit = load_pdfs()
    questions = load_quiz()
    total_docs = sum(len(v) for v in pdfs_by_unit.values())

    # Build all HTML parts as a list
    parts = []

    parts.append('''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Empleabilidad — Guía Interactiva Parte 1</title>
<style>
:root{--bg:#0a0f1f;--card:#111827;--card2:#1a2332;--a:#00d4aa;--a2:#7c5bf0;--t:#e8ecf5;--t2:#8892b0;--b:#4a9eff;--y:#f5c842;--o:#ff9f43}
*{margin:0;padding:0;box-sizing:border-box;scroll-behavior:smooth}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--t);min-height:100vh}
::selection{background:rgba(0,212,170,.25)}
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
.hero h2{font-size:18px;font-weight:700;margin-bottom:5px}.hero h2 .c{color:var(--a)}
.hero p{color:var(--t2);font-size:12px}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.badge{padding:3px 9px;border-radius:5px;font-size:10px;font-weight:500}
.b1{background:rgba(0,212,170,.12);color:var(--a)}
.b2{background:rgba(74,158,255,.12);color:var(--b)}
.b3{background:rgba(124,91,240,.12);color:var(--a2)}
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
.cbody{padding:2px 6px}.cbody p{font-size:12px;line-height:1.65;color:var(--t2);margin-bottom:6px}
.cbody ul{list-style:none;padding:0 4px}.cbody ul li{font-size:12px;color:var(--t2);padding:3px 0 3px 18px;position:relative;line-height:1.5}
.cbody ul li::before{content:"\\25B8";position:absolute;left:2px;color:var(--a);font-weight:700}
.tbl{overflow-x:auto;margin:6px 0;border-radius:6px;font-size:11px}
.tbl table{width:100%;border-collapse:collapse}
.tbl th{background:var(--card2);color:var(--a);padding:6px 10px;text-align:left;font-weight:600;border-bottom:1px solid rgba(0,212,170,.15);white-space:nowrap;font-size:11px}
.tbl td{padding:5px 10px;border-bottom:1px solid rgba(255,255,255,.04);color:var(--t2);vertical-align:top}
.tbl tr:hover td{background:rgba(0,212,170,.03)}
a{color:var(--a);text-decoration:none}a:hover{text-decoration:underline}
.done{text-align:center;padding:60px 20px;font-size:20px;color:var(--t2)}
.done #fs{font-size:28px;display:block;margin-top:14px;color:var(--a);font-weight:700}
.quiz-container{background:var(--card);border-radius:12px;padding:18px;border:1px solid rgba(255,255,255,.04)}
.qheader{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.qmeta{color:var(--t2);font-size:13px;font-weight:600}
.card{max-width:600px;margin:0 auto;padding:20px 0}.card-q{background:var(--card2);border-radius:12px;padding:28px 20px;border:1px solid rgba(255,255,255,.06);text-align:center;margin-bottom:18px}
.card-num{display:inline-block;background:var(--a);color:#0a0e1a;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;margin-bottom:14px}
.card-q h3{font-size:16px;line-height:1.5;margin:0}
.card-answer{text-align:center}
.reveal-btn{padding:14px 32px;border:2px solid var(--a);border-radius:10px;background:rgba(0,212,170,.08);color:var(--a);font-size:14px;font-weight:700;cursor:pointer;transition:.2s}
.reveal-btn:hover{background:var(--a);color:#0a0e1a;transform:translateY(-2px)}
.answer-text{background:rgba(0,212,170,.1);border:1px solid rgba(0,212,170,.2);border-radius:10px;padding:20px;font-size:15px;line-height:1.5;color:var(--t);margin-top:14px}
.tag{display:inline-block;background:var(--a);color:#0a0e1a;font-size:10px;font-weight:700;padding:2px 10px;border-radius:20px;margin-bottom:10px}
.next-btn{padding:12px 28px;border:none;border-radius:10px;background:linear-gradient(135deg,var(--a),#00b894);color:#0a0e1a;font-size:14px;font-weight:700;cursor:pointer;margin-top:16px;transition:.2s}
.next-btn:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,212,170,.25)}
.lib-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}
.doc-link{display:flex;flex-direction:column;gap:4px;padding:12px 14px;background:var(--card);border-radius:10px;border:1px solid rgba(255,255,255,.04);text-decoration:none;transition:.2s}
.doc-link:hover{border-color:var(--a);background:var(--card2);transform:translateY(-2px)}
.doc-link .dn{font-size:12px;font-weight:600;color:var(--t);line-height:1.4}
.doc-link .ds{font-size:10px;color:var(--t2)}
.st{position:fixed;bottom:20px;right:20px;width:36px;height:36px;border-radius:50%;background:var(--a);color:#0a0e1a;border:none;cursor:pointer;font-size:18px;opacity:0;transition:.3s;pointer-events:none;z-index:50;box-shadow:0 3px 12px rgba(0,212,170,.3)}
.st.v{opacity:1;pointer-events:auto}
@media(max-width:768px){.topbar{padding:10px 14px}.searchbox{width:100%;margin-top:6px}.searchbox:focus{width:100%}.nav{top:92px;padding:8px 12px}.main{padding:10px 12px}.hero{padding:14px 16px}.hero h2{font-size:15px}.sech{padding:10px 12px;font-size:12px}.lib-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="topbar"><div><h1>\U0001f4cb Empleabilidad</h1><div class="sub">Guía interactiva de estudio ''')
    parts.append(f"&bull; {len(UNITS)} unidades &bull; {len(questions)} preguntas")
    parts.append('''</div></div><input class="searchbox" id="s" placeholder="🔍 Buscar..." oninput="su(this.value)"></div>
<div class="nav" id="nav">''')

    # Navigation buttons
    for idx, unit in enumerate(UNITS):
        active = " active" if idx == 0 else ""
        short = unit["title"][:30]
        parts.append(f'<button class="nav-btn{active}" onclick="x({idx})"><b>{unit["id"]}</b> {esc(short)}&hellip;</button>')
    parts.append(f'<button class="nav-btn" onclick="x({len(UNITS)})"><b>\U0001f4dd</b> Cuestionario</button>')
    parts.append(f'<button class="nav-btn" onclick="x({len(UNITS)+1})"><b>\U0001f4da</b> Documentos</button>')

    parts.append('''</div>
<div class="main" id="m">''')

    # Units
    for idx, unit in enumerate(UNITS):
        uid = unit["id"]
        docs = pdfs_by_unit.get(uid, [])
        docs.sort(key=lambda d: "Síntesis" not in d["title"])
        active_class = " active" if idx == 0 else ""

        topics_str = ", ".join(unit["topics"])
        parts.append(f'''<div class="unit{active_class}" id="u{idx}">
<div class="hero"><h2>{unit["emoji"]} <span class="c">{uid}:</span> {esc(unit["title"])}</h2>
<p>{esc(topics_str)}</p>
<div class="badges"><span class="badge b1">\U0001f4d6 {len(unit["topics"])} temas</span><span class="badge b2">\U0001f4c4 {len(docs)} documentos</span></div>
</div>
<div class="secc"><div class="sech" onclick="t(this)"><span class="arrow">\u25b6</span><span class="num">{uid}</span>{esc(unit["title"])}</div>
<div class="secb"><div class="stitle purple">\U0001f4cc Temas principales</div>
<div class="cbody"><ul>''')

        for topic in unit["topics"]:
            parts.append(f"<li>{esc(topic)}</li>")

        parts.append('</ul></div></div></div>')

        if docs:
            rows = ""
            for d in docs:
                rows += f'''<tr><td>{esc(d["title"][:70])}</td><td>{d["size"]}</td><td><a href="{esc(d["file"])}" target="_blank" rel="noopener">PDF \U0001f4c4</a></td></tr>'''
            parts.append(f'''<div class="secc"><div class="sech" onclick="t(this)"><span class="arrow">\u25b6</span><span class="num">\U0001f4ce</span>Documentos fuente</div>
<div class="secb"><div class="tbl"><table><tr><th>Documento</th><th>Tama\u00f1o</th><th>Abrir</th></tr>{rows}</table></div></div></div>''')

        parts.append('</div>')

    # Quiz section
    qjson_str = json.dumps(questions, ensure_ascii=False)
    q_count = len(questions)
    parts.append(f'''<div class="unit" id="u{len(UNITS)}">
<div class="hero"><h2>\U0001f4dd <span class="c">Cuestionario</span> de repaso</h2>
<p>{q_count} preguntas sobre Empleabilidad Parte 1 &middot; Pulsa para ver la respuesta</p>
<div class="badges"><span class="badge b1">\U0001f4dd {q_count} preguntas</span><span class="badge b3">Estudio</span></div>
</div>
<div class="quiz-container"><div class="qheader"><div class="qmeta"><span id="qp">0</span> / {q_count} &middot; <span id="qs">0</span> vistas</div><button class="navb" onclick="rq()">\U0001f504 Reiniciar</button></div><div id="ql"></div></div>
</div>''')

    # Document library
    doc_count = total_docs
    parts.append(f'''<div class="unit" id="u{len(UNITS)+1}">
<div class="hero"><h2>\U0001f4da <span class="c">Biblioteca</span> de documentos</h2>
<p>Todos los PDFs de la Parte 1 organizados por unidad</p>
<div class="badges"><span class="badge b1">\U0001f4c4 {doc_count} documentos</span></div>
</div>
<div class="lib-grid">''')

    for unit_key in sorted(pdfs_by_unit.keys()):
        docs = pdfs_by_unit[unit_key]
        for d in docs:
            parts.append(f'''<a class="doc-link" href="{esc(d["file"])}" target="_blank" rel="noopener"><span class="dn">{esc(d["title"][:60])}</span><span class="ds">{d["size"]}</span></a>''')

    parts.append('</div></div></div>')

    # Footer and scripts
    parts.append('''<button class="st" id="st" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="Subir">&uarr;</button>
<script>
const Q = ''')
    parts.append(qjson_str)
    parts.append(''';
let qi = 0, sc = 0, ui = 0;
const un = document.querySelectorAll('.unit'), nb = document.querySelectorAll('.nav-btn');

function x(i) {
  if (document.getElementById('u' + ui)) document.getElementById('u' + ui).classList.remove('active');
  if (nb[ui]) nb[ui].classList.remove('active');
  ui = i;
  const el = document.getElementById('u' + i);
  if (el) el.classList.add('active');
  if (nb[i]) { nb[i].classList.add('active'); nb[i].scrollIntoView({behavior:'smooth',inline:'center',block:'nearest'}); }
  window.scrollTo({top:0,behavior:'smooth'});
}

function t(el) {
  const b = el.nextElementSibling;
  const a = el.querySelector('.arrow');
  if (b && b.classList.contains('secb')) { b.classList.toggle('open'); if (a) a.classList.toggle('o'); }
}

function su(v) {
  const q = v.toLowerCase();
  document.querySelectorAll('.secc').forEach(s => {
    s.style.display = s.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

function rq() { qi = 0; sc = 0; document.getElementById('qs').textContent = '0'; r(); }

function r() {
  if (qi >= Q.length) {
    document.getElementById('ql').innerHTML = '<div class="done">\\u2705 \\u00a1Completaste las ' + Q.length + ' preguntas!<br><span id="fs">' + sc + '/' + Q.length + ' vistas</span></div>';
    document.getElementById('qp').textContent = Q.length;
    return;
  }
  const q = Q[qi];
  document.getElementById('qp').textContent = qi + 1;
  let h = '<div class="card"><div class="card-q"><span class="card-num">' + (qi+1) + '</span><h3>' + q.pregunta + '</h3></div>';
  h += '<div class="card-answer" id="ans">';
  h += '<button class="reveal-btn" onclick="showAns()">\\u2709 Pulsa para ver la respuesta</button>';
  h += '<div class="answer-text" id="at" style="display:none"><span class="tag">Respuesta correcta</span>' + q.respuesta_correcta + '</div>';
  h += '</div></div>';
  document.getElementById('ql').innerHTML = h;
  document.getElementById('qs').textContent = sc;
}

function showAns() {
  document.getElementById('ans').innerHTML = '<div class="card-answer"><div class="answer-text" style="display:block"><span class="tag">Respuesta correcta</span>' + Q[qi].respuesta_correcta + '</div><button class="next-btn" onclick="nextQ()">Siguiente \\u2192</button></div>';
}

function nextQ() { sc++; document.getElementById('qs').textContent = sc; qi++; r(); }

window.addEventListener('scroll', () => {
  const s = document.getElementById('st');
  if (window.scrollY > 300) s.classList.add('v'); else s.classList.remove('v');
});

r();
</script>
</body>
</html>''')

    result = "".join(parts)
    OUT.write_text(result, encoding="utf-8")
    print(f"✅ Generated {OUT}")
    print(f"   • {len(UNITS)} units")
    print(f"   • {total_docs} documents")
    print(f"   • {len(questions)} quiz questions")


if __name__ == "__main__":
    build()
