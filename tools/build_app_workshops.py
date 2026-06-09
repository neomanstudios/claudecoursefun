#!/usr/bin/env python3
"""Render the broad AI-skills workshops into the dark LMS player (app/workshops/).
Reuses the dark shell + tokens from app/app.css and behaviours from app/app.js
(tabs, quiz, complete, the guided stepper, the agent demo). Workshops are organised
by 7 colour-coded categories. Hands-on steps render as the dark one-step-at-a-time
stepper; embedded prompts become inline copy-trays."""
import os, html, json
from build_app import strip_emoji, FONTS, prompt_tray

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "app", "workshops")
catalog = json.load(open(os.path.join(ROOT, "data", "workshops.json"), encoding="utf-8"))
cpath = os.path.join(ROOT, "data", "workshops_content.json")
content = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}

FLAT = [(c, w) for c in catalog["categories"] for w in c["workshops"]]
READY = [(c, w) for c, w in FLAT if w["slug"] in content]

# category colour -> dark hex accent (used via --mc)
MC = {"m1": "#FB7185", "m2": "#FBBF24", "m3": "#F472B6", "m4": "#38BDF8",
      "m5": "#34D399", "m6": "#EC4899", "m7": "#818CF8", "m8": "#2DD4BF"}
def mc(cat): return MC.get(cat.get("color", "m4"), "#38BDF8")

RING = ('<div class="ring"><svg viewBox="0 0 36 36"><circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="3.4"/>'
        '<circle class="ring-i" cx="18" cy="18" r="15.5" fill="none" stroke="url(#rg)" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="0 100" transform="rotate(-90 18 18)"/>'
        '<text class="ring-t" x="18" y="21" text-anchor="middle" font-size="8.5" font-weight="800" fill="#EAEEF9" font-family="Plus Jakarta Sans">0%</text>'
        '<defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3B82F6"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient></defs></svg>'
        '<div class="rlbl">ความคืบหน้าเวิร์กช็อป</div></div>')

def topbar():
    return ('<header class="topbar"><button class="hamb" aria-label="เมนู"><svg class="ic" viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>'
            '<span class="tb-here">เวิร์กช็อป</span></header>')

# ---------- sidebar (categories -> workshops) ----------
def ws_outline(active_slug):
    rows = []
    for c in catalog["categories"]:
        op = " open" if any(w["slug"] == active_slug for w in c["workshops"]) else ""
        lis = []
        for w in c["workshops"]:
            has = w["slug"] in content
            if has:
                cls = " active" if w["slug"] == active_slug else ""
                lis.append(f'<li><a href="{w["slug"]}.html" data-slug="{w["slug"]}" class="{cls.strip()}">'
                           f'<span class="dot"></span><span class="lt">{html.escape(w["title"])}</span></a></li>')
            else:
                lis.append(f'<li><span class="ws-soon"><span class="dot"></span>'
                           f'<span class="lt">{html.escape(w["title"])}</span><em>เร็ว ๆ นี้</em></span></li>')
        rows.append(f'<details class="mod"{op} style="--mc:{mc(c)}"><summary><span class="mn">{c["num"]}</span>'
                    f'<span class="mt">{html.escape(c["title"])}</span>'
                    f'<svg class="chev ic" viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"/></svg></summary>'
                    f'<ul class="lessons">{"".join(lis)}</ul></details>')
    return ('<aside class="sidebar"><div class="brand"><a href="index.html" class="brand-l">'
            '<span class="logo">CC</span><b>Workshops</b></a></div>'
            '<div class="sb-progress"><div class="pl"><span>ทำเสร็จแล้ว</span><b class="prog-lbl">0/0</b></div>'
            '<div class="pbar"><i></i></div></div>'
            f'<div class="sb-scroll">{"".join(rows)}</div>'
            '<a class="sb-back" href="../index.html"><svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="m15 18-6-6 6-6"/></svg>คอร์ส Claude Code</a></aside>')

# ---------- blocks ----------
def _sec(heading, lead, sid):
    h = f'<h3 class="sec-title" id="{sid}">{html.escape(heading)}</h3>' if heading else ""
    l = f'<p class="sec-lead">{html.escape(lead)}</p>' if lead else ""
    return h + l

def block_glance(g):
    chips = "".join(f'<span class="chip">{c}</span>' for c in g.get("chips", []))
    return (f'<div class="glance"><div class="glance-t"><svg class="ic" viewBox="0 0 24 24" style="width:15px"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>รู้ใน 30 วิ</div>'
            f'<p>{g["summary"]}</p><div class="glance-chips">{chips}</div></div>')

def block_compare(b, sid):
    cards = ""
    for it in b["items"]:
        lvl = int(it.get("level", 1))
        meter = "".join('<i class="on"></i>' if i < lvl else '<i></i>' for i in range(3))
        best = " is-best" if it.get("best") else ""
        vc = it.get("color", "var(--accent)")
        cards += (f'<div class="vs{best}" style="--vc:{vc}"><div class="vs-ic">{it.get("icon","")}</div>'
                  f'<div class="vs-name">{html.escape(it["name"])}</div>'
                  f'<div class="vs-role">{it["role"]}</div>'
                  f'<div class="meter">{meter}<span>{html.escape(it.get("label",""))}</span></div></div>')
    return _sec(b.get("heading"), b.get("lead"), sid) + f'<div class="vs-grid">{cards}</div>'

def block_concept(b, sid):
    cards = ""
    for i, it in enumerate(b["items"], 1):
        cards += (f'<div class="concept"><div class="c-num">{i}</div>'
                  f'<h4>{html.escape(it["title"])}</h4><p>{it["body"]}</p></div>')
    return _sec(b.get("heading"), b.get("lead"), sid) + f'<div class="concept-grid">{cards}</div>'

def block_keypoint(b, sid):
    return (f'<div class="keypoint"><span class="kp-i"><svg class="ic" viewBox="0 0 24 24" style="width:17px">'
            f'<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2h6c0-.8.4-1.5 1-2A7 7 0 0 0 12 2Z"/></svg></span>'
            f'<p>{b["text"]}</p></div>')

def block_howto(b, sid):
    """Dark guided stepper: emit .steps[data-stepper] matching initSteps() in app.js.
    A step may be a string, or {text, prompt} to embed a copyable prompt IN the step."""
    lis = []
    for s in b["steps"]:
        if isinstance(s, dict):
            inner = f'<div class="st-d">{s.get("text","")}</div>' + (prompt_tray(s["prompt"]) if s.get("prompt") else "")
        else:
            inner = f'<div class="st-d">{s}</div>'
        lis.append(f'<li class="step"><div class="st-main">{inner}</div></li>')
    n = len(b["steps"])
    attr = ' data-stepper' if n >= 2 else ''
    badge = f'<span class="ho-badge">{html.escape(b["badge"])}</span>' if b.get("badge") else ""
    title = html.escape(b.get("title", "ลองเลย"))
    return (f'<div class="howto-wrap"><div class="howto-t" id="{sid}">'
            f'<svg class="ic" viewBox="0 0 24 24" style="width:18px;color:var(--accent-2)"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>'
            f'{title}{badge}</div><ol class="steps"{attr}>{"".join(lis)}</ol></div>')

def block_prompt(b, sid):
    pid = f"pt-{sid}"
    return (f'<div class="prompt-box"><div class="prompt-label">{html.escape(b.get("label","ลองใช้ Prompt นี้"))}</div>'
            f'<div class="prompt-text" id="{pid}">{html.escape(b["text"])}</div>'
            f'<button class="copy-btn" onclick="cp(\'{pid}\')">คัดลอก Prompt</button></div>')

def block_agentdemo(b, sid):
    steps = "".join(f'<li><span class="st">{html.escape(s.get("icon","›"))}</span><span>{s["text"]}</span></li>' for s in b["steps"])
    return (_sec(b.get("heading"), b.get("lead"), sid) + '<div class="agentdemo">'
            f'<div class="agentdemo-head"><span class="ad-dot"></span><span class="ad-dot"></span><span class="ad-dot"></span>'
            f'<span class="ad-t">{html.escape(b.get("title","ดู Claude Code ทำงาน"))}</span>'
            f'<button class="ad-run" type="button">รัน</button></div>'
            f'<div class="ad-prompt"><span class="lbl">คุณ</span><span>{b["prompt"]}</span></div>'
            f'<ul class="ad-log">{steps}</ul></div>')

RENDERERS = {"compare": block_compare, "concept": block_concept, "keypoint": block_keypoint,
             "howto": block_howto, "prompt": block_prompt, "agentdemo": block_agentdemo}

def render_blocks(blocks):
    out, toc = "", []
    for i, b in enumerate(blocks, 1):
        sid = f"sec-{i}"
        out += RENDERERS[b["type"]](b, sid)
        if b.get("heading"):
            toc.append((sid, b["heading"]))
        elif b["type"] == "howto":
            toc.append((sid, b.get("title", "ลองเลย")))
    return out, toc

def ws_quiz(qs):
    if not qs: return ""
    rows = []
    for i, q in enumerate(qs, 1):
        ch = "".join(f'<button class="choice"><span class="mk">{"ABCD"[j]}</span><span>{html.escape(c)}</span></button>'
                     for j, c in enumerate(q["choices"]))
        rows.append(f'<div class="q" data-answer="{q["answer"]}"><div class="q-text">'
                    f'<span class="qn">ข้อ {i}.</span>{html.escape(q["q"])}</div>'
                    f'<div class="choices">{ch}</div>'
                    f'<div class="q-explain"><strong>เฉลย:</strong> {html.escape(q.get("explain",""))}</div></div>')
    return ('<div class="quiz"><div class="quiz-h">แบบทดสอบท้ายเวิร์กช็อป</div>'
            f'<div class="quiz-sub">ลองตอบดู แล้วระบบจะเฉลยให้ทันที</div>{"".join(rows)}</div>')

def ws_takeaways(items):
    if not items: return ""
    lis = "".join(f"<li>{t}</li>" for t in items)
    return f'<div class="takeaways"><div class="tk-title">สรุปเวิร์กช็อป</div><ul>{lis}</ul></div>'

def cover(cat, w):
    img = f"../../images/{w['slug']}.webp"
    if not os.path.exists(os.path.join(ROOT, "images", w["slug"] + ".webp")):
        return ""
    style = f"background-image:linear-gradient(90deg,rgba(8,11,22,.92),rgba(8,11,22,.35)),url('{img}')"
    return (f'<div class="cover" style="{style}"><div class="ctxt"><div class="k">{html.escape(cat["num"])} · {html.escape(cat["title"])}</div>'
            f'<h2>{html.escape(w["title"])}</h2></div></div>')

def navbtn(idx, nxt):
    if idx < 0 or idx >= len(READY): return ""
    _, w = READY[idx]
    d = "เวิร์กช็อปถัดไป &#8594;" if nxt else "&#8592; ก่อนหน้า"
    cls = "pn-a nx" if nxt else "pn-a"
    return f'<a class="{cls}" href="{w["slug"]}.html"><span class="d">{d}</span><span class="t">{html.escape(w["title"])}</span></a>'

def render_workshop(cat, w):
    c = content[w["slug"]]
    body, toc = render_blocks(c["blocks"])
    qz = ws_quiz(c.get("quiz"))
    toc_links = "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t in toc)
    i = next((k for k, (_, x) in enumerate(READY) if x["slug"] == w["slug"]), 0)
    prev_b = navbtn(i-1, False) or '<span class="pn-a disabled"><span class="d">&#8592; ก่อนหน้า</span><span class="t">นี่คืออันแรก</span></span>'
    next_b = navbtn(i+1, True) or '<span class="pn-a nx disabled"><span class="d">เวิร์กช็อปถัดไป &#8594;</span><span class="t">ครบแล้ว</span></span>'
    tabs = ('<div class="tabs"><button class="on" data-tab="overview">เนื้อหา</button>'
            + ('<button data-tab="quiz">แบบทดสอบ</button>' if qz else '') + '</div>')
    quiz_panel = f'<section class="tab-panel" data-panel="quiz" hidden>{qz}</section>' if qz else ''
    return f"""<!DOCTYPE html>
<html lang="th">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(w["title"])} | Workshops</title>
<meta name="description" content="{html.escape(w.get('goal','')[:150])}">
<script>(function(){{try{{var t=localStorage.getItem('cc_app_theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}document.documentElement.className+=' js';}})();</script>
{FONTS}<link rel="stylesheet" href="../app.css"></head>
<body data-slug="{w['slug']}">
<div class="sb-overlay"></div>
{ws_outline(w['slug'])}
<div class="shell">
{topbar()}
<div class="content">
<div class="main">
<div class="crumb"><a class="back" href="index.html"><svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="m15 18-6-6 6-6"/></svg>เวิร์กช็อป</a><span class="sep">&#8250;</span>{html.escape(cat['title'])}</div>
<div class="les-head"><div><span class="ws-badge" style="--mc:{mc(cat)}">{html.escape(cat['num'])} · {html.escape(cat['title'])}</span><h1>{html.escape(w['title'])}</h1><p>{html.escape(w.get('goal',''))}</p></div>
{RING}</div>
{cover(cat, w)}
{tabs}
<section class="tab-panel" data-panel="overview">
<div class="ov"><div class="ov-main">{block_glance(c['glance'])}{body}{ws_takeaways(c.get('takeaways'))}
<div class="complete-row"><button class="btn-complete" id="btnComplete">ทำเครื่องหมายว่าเรียนจบ</button></div></div>
<aside class="ov-side">{f'<div class="card toc"><div class="toc-t">ในเวิร์กช็อปนี้</div>{toc_links}{"<a href=#quiz class=tq>แบบทดสอบ</a>" if qz else ""}</div>' if toc_links else ''}</aside></div>
</section>
{quiz_panel}
<div class="pn">{prev_b}{next_b}</div>
</div>
</div></div>
<script src="../app.js"></script></body></html>"""

def build_index():
    cards = []
    for c in catalog["categories"]:
        ready = sum(1 for w in c["workshops"] if w["slug"] in content)
        lis = []
        for w in c["workshops"]:
            if w["slug"] in content:
                lis.append(f'<li><a href="{w["slug"]}.html" data-slug="{w["slug"]}"><span class="dot"></span>'
                           f'<span class="lt">{html.escape(w["title"])}</span></a></li>')
            else:
                lis.append(f'<li><span class="ws-soon"><span class="dot"></span>'
                           f'<span class="lt">{html.escape(w["title"])}</span><em>เร็ว ๆ นี้</em></span></li>')
        cards.append(f'<section class="mcard" style="--mc:{mc(c)}"><div class="mc-h"><span class="mn">{c["num"]}</span>'
                     f'<div><h3>{html.escape(c["title"])}</h3><p>{len(c["workshops"])} เวิร์กช็อป · พร้อม {ready}</p></div></div>'
                     f'<ul class="lessons mc-list">{"".join(lis)}</ul></section>')
    total = len(FLAT)
    ready_total = len(READY)
    page = f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Workshops | ทำงานจริงด้วย AI</title>
<script>(function(){{try{{var t=localStorage.getItem('cc_app_theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}document.documentElement.className+=' js';}})();</script>
{FONTS}<link rel="stylesheet" href="../app.css"></head>
<body data-slug="__wshome__">
<div class="sb-overlay"></div>
{ws_outline(None)}
<div class="shell">
{topbar()}
<div class="home">
<div class="hero"><div class="k">เวิร์กช็อปลงมือทำ</div><h1>ทำงานจริงด้วย <em>AI</em> ทีละขั้น</h1>
<p>{total} เวิร์กช็อปสั้น ๆ จับมือทำใน 7 หมวด ใช้ Claude Code เป็นตัวหลัก เรียกเครื่องมืออื่นเฉพาะตอนที่มันทำเองไม่ได้ · พร้อมแล้ว {ready_total} เวิร์กช็อป</p>
<a class="cta" href="../index.html">&#8592; กลับไปคอร์ส Claude Code</a></div>
<h2 class="sec">หมวดเวิร์กช็อป</h2>
<div class="mgrid">{''.join(cards)}</div>
</div></div>
<script src="../app.js"></script></body></html>"""
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
    print("built app/workshops/index.html")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for cat, w in READY:
        open(os.path.join(OUT, w["slug"] + ".html"), "w", encoding="utf-8").write(render_workshop(cat, w))
        n += 1
    build_index()
    print(f"built {n} dark workshop pages (of {len(FLAT)})")
