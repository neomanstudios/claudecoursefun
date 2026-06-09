#!/usr/bin/env python3
"""Render hands-on workshops from data/workshops.json + data/workshops_content.json
into workshops/*.html using the shared infographic format (assets/app.css)."""
import os, json, html
from build_site import (FONTS, HEAD_THEME, theme_toggle, strip_lead_emoji,
                        declutter_labels)

ROOT = os.path.join(os.path.dirname(__file__), "..")
catalog = json.load(open(os.path.join(ROOT, "data", "workshops.json"), encoding="utf-8"))
content = json.load(open(os.path.join(ROOT, "data", "workshops_content.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(ROOT, "data", "workshops_content.json")) else {}

FLAT = [(c, w) for c in catalog["categories"] for w in c["workshops"]]

# Prose fields (glance summary, chips, compare role, concept body, keypoint text,
# howto steps, takeaways) are trusted authored HTML and inserted raw so they may use
# <b>/<code>. Labels/identifiers (names, titles, headings, labels, quiz text) are escaped.
def _sec(heading, lead, sid):
    h = f'<h2 class="sec-title" id="{sid}">{html.escape(heading)}</h2>' if heading else ""
    l = f'<p class="sec-lead">{html.escape(lead)}</p>' if lead else ""
    return h + l

def block_glance(g):
    chips = "".join(f'<span class="chip">{c}</span>' for c in g.get("chips", []))
    return (f'<div class="glance"><div class="glance-t">รู้ใน 30 วิ</div>'
            f'<p>{g["summary"]}</p><div class="glance-chips">{chips}</div></div>')

def block_compare(b, sid):
    cards = ""
    for it in b["items"]:
        lvl = int(it.get("level", 1))
        meter = "".join('<i class="on"></i>' if i < lvl else '<i></i>' for i in range(3))
        best = " is-best" if it.get("best") else ""
        vc = it.get("color", "var(--mc)")
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
    return f'<div class="keypoint"><p>{b["text"]}</p></div>'

def block_howto(b, sid):
    steps = "".join(f'<li><div class="ht">{s}</div></li>' for s in b["steps"])
    badge = f'<span class="badge">{html.escape(b["badge"])}</span>' if b.get("badge") else ""
    title = html.escape(b.get("title", "ลองเลย"))
    return (f'<div class="howto"><div class="howto-t" id="{sid}">{title} {badge}</div>'
            f'<ol>{steps}</ol></div>')

def block_prompt(b, sid):
    return (f'<div class="prompt-box"><div class="prompt-label">{html.escape(b.get("label","ลองใช้ Prompt นี้"))}</div>'
            f'<div class="prompt-text" id="{sid}">{html.escape(b["text"])}</div>'
            f'<button class="copy-btn" onclick="cp(\'{sid}\')">คัดลอก Prompt</button></div>')

def block_agentdemo(b, sid):
    # interactive: learner clicks Run and watches Claude Code work through the task.
    steps = "".join(f'<li><span class="st">{html.escape(s.get("icon", "›"))}</span>'
                    f'<span>{s["text"]}</span></li>' for s in b["steps"])
    return (_sec(b.get("heading"), b.get("lead"), sid) + '<div class="agentdemo">'
            f'<div class="agentdemo-head"><span class="ad-t">{html.escape(b.get("title", "ดู Claude Code ทำงาน"))}</span>'
            f'<button class="ad-run" type="button">▶ รัน</button></div>'
            f'<div class="ad-prompt"><span class="lbl">คุณ</span><span>{b["prompt"]}</span></div>'
            f'<ul class="ad-log">{steps}</ul></div>')

RENDERERS = {"compare": block_compare, "concept": block_concept,
             "keypoint": block_keypoint, "howto": block_howto, "prompt": block_prompt,
             "agentdemo": block_agentdemo}

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
        ch = "".join(f'<button class="choice"><span class="mk">{"ABCD"[j]}</span>'
                     f'<span>{html.escape(c)}</span></button>' for j, c in enumerate(q["choices"]))
        rows.append(f'<div class="q" data-answer="{q["answer"]}"><div class="q-text">'
                    f'<span class="qn">ข้อ {i}.</span>{html.escape(q["q"])}</div>'
                    f'<div class="choices">{ch}</div>'
                    f'<div class="q-explain"><strong>เฉลย:</strong> {html.escape(q.get("explain",""))}</div></div>')
    return ('<div class="quiz" id="quiz"><div class="quiz-h">แบบทดสอบท้ายเวิร์กช็อป</div>'
            f'<div class="quiz-sub">ลองตอบดู แล้วระบบจะเฉลยให้ทันที</div>{"".join(rows)}</div>')

def ws_takeaways(items):
    if not items: return ""
    lis = "".join(f"<li>{t}</li>" for t in items)
    return f'<div class="takeaways"><div class="tk-title">สรุปเวิร์กช็อป</div><ul>{lis}</ul></div>'

def ws_sidebar(active_slug):
    rows = []
    for c in catalog["categories"]:
        active_in = any(w["slug"] == active_slug for w in c["workshops"])
        op = " open" if active_in else ""
        lis = []
        for w in c["workshops"]:
            has = w["slug"] in content
            cls = "active" if w["slug"] == active_slug else ("" if has else "soon")
            if has:
                lis.append(f'<li><a href="{w["slug"]}.html" data-slug="{w["slug"]}" class="{cls}">'
                           f'<span class="dot"></span><span>{html.escape(w["title"])}</span></a></li>')
            else:
                lis.append(f'<li><span class="sb-soon"><span class="dot"></span>'
                           f'<span>{html.escape(w["title"])}</span><em>เร็ว ๆ นี้</em></span></li>')
        rows.append(f'<details class="sb-mod" data-mod="{c["color"][1:]}"{op}><summary>'
                    f'<span class="mn">{c["num"]}</span><span class="mt">{html.escape(c["title"])}</span>'
                    f'<span class="mk">▶</span></summary><ul class="sb-les">{"".join(lis)}</ul></details>')
    return ('<aside class="sidebar"><div class="sb-head">'
            '<a href="index.html" class="sb-brand-link"><span class="sb-logo">⚡</span>'
            '<span class="sb-brand">Claude Code<small>เวิร์กช็อปลงมือทำ</small></span></a>'
            f'{theme_toggle()}</div>'
            f'<nav class="sb-nav">{"".join(rows)}</nav>'
            '<div class="sb-back"><a href="../index.html">← คอร์ส Claude Code</a></div></aside>')

def render_workshop(cat, w):
    c = content[w["slug"]]
    body, toc = render_blocks(c["blocks"])
    body = declutter_labels(body)
    toc_links = "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t in toc)
    if c.get("quiz"):
        toc_links += '<a href="#quiz" class="toc-quiz">แบบทดสอบ</a>'
    img = f'../images/{w["slug"]}.webp'
    fig = (f'<figure class="lesson-hero"><img src="{img}" alt="{html.escape(w["title"])}" '
           f'loading="lazy" decoding="async"></figure>') if os.path.exists(
           os.path.join(ROOT, "images", w["slug"] + ".webp")) else ""
    return f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(w["title"])} | Claude Code Workshops</title>
<meta name="description" content="{html.escape(w["goal"])}">
{HEAD_THEME}{FONTS}<link rel="stylesheet" href="../assets/app.css"></head>
<body data-slug="{w["slug"]}" data-mod="{cat["color"][1:]}">
<div class="reading-bar" id="bar"></div><div class="sb-overlay"></div>
{ws_sidebar(w["slug"])}
<div class="main"><div class="topbar"><button class="hamb" id="hamb" aria-label="เมนู">☰</button>
<span class="tb-title">{html.escape(cat["title"])}</span>{theme_toggle()}</div>
<div class="docs"><article class="reading">
<div class="crumb"><a href="index.html">เวิร์กช็อป</a> › {html.escape(cat["title"])}</div>
<span class="les-no">{html.escape(cat["title"])}</span>
<h1>{html.escape(w["title"])}</h1>
{block_glance(c["glance"])}
{fig}
{body}
{ws_takeaways(c.get("takeaways"))}
{ws_quiz(c.get("quiz"))}
<div class="complete-row"><button class="btn-complete" id="btnComplete">✓ ทำเครื่องหมายว่าเรียนจบ</button></div>
</article><aside class="toc"><div class="toc-t">ในเวิร์กช็อปนี้</div>{toc_links}</aside></div>
<footer>Claude Code Workshops</footer></div>
<script src="../assets/app.js"></script></body></html>"""

def build_workshops():
    out = os.path.join(ROOT, "workshops")
    os.makedirs(out, exist_ok=True)
    n = 0
    for cat, w in FLAT:
        if w["slug"] not in content:
            continue
        open(os.path.join(out, w["slug"] + ".html"), "w", encoding="utf-8").write(render_workshop(cat, w))
        n += 1
    print(f"built {n} workshop pages")

def build_workshops_index():
    cards = []
    for c in catalog["categories"]:
        ready = sum(1 for w in c["workshops"] if w["slug"] in content)
        lis = []
        for w in c["workshops"]:
            if w["slug"] in content:
                lis.append(f'<li><a href="{w["slug"]}.html" data-slug="{w["slug"]}">'
                           f'<span class="dot"></span><span>{html.escape(w["title"])}</span></a></li>')
            else:
                lis.append(f'<li><span class="sb-soon"><span class="dot"></span>'
                           f'<span>{html.escape(w["title"])}</span><em>เร็ว ๆ นี้</em></span></li>')
        cards.append(f'<section class="mod-card reveal" data-mod="{c["color"][1:]}">'
                     f'<div class="mc-head"><span class="mn">{c["num"]}</span>'
                     f'<div><h3>{html.escape(c["title"])}</h3>'
                     f'<p>{len(c["workshops"])} เวิร์กช็อป · พร้อม {ready}</p></div></div>'
                     f'<ul class="mc-list">{"".join(lis)}</ul></section>')
    total = len(FLAT)
    page = f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code Workshops | ลงมือทำจริง</title>
<meta name="description" content="{total} เวิร์กช็อปลงมือทำกับ Claude Code">
{HEAD_THEME}{FONTS}<link rel="stylesheet" href="../assets/app.css"></head>
<body data-slug="__wshome__">
<div class="reading-bar" id="bar"></div><div class="sb-overlay"></div>
{ws_sidebar(None)}
<div class="main"><div class="topbar"><button class="hamb" id="hamb" aria-label="เมนู">☰</button>
<span class="tb-title">Claude Code Workshops</span>{theme_toggle()}</div>
<div class="home"><section class="home-hero">
<span class="tag">ทำงานจริงด้วย Claude Code</span>
<h1>เรียนทำงานจริงด้วย Claude Code</h1>
<p>เวิร์กช็อปสั้น ๆ จับมือทำ ใช้ Claude Code เป็นตัวหลักในทุกงาน เรียกเครื่องมืออื่นเฉพาะตอนที่มันทำเองไม่ได้ เช่น สร้างรูป</p>
<div class="home-stats"><div><b>{total}</b> เวิร์กช็อป</div><div><b>{len(catalog['categories'])}</b> หมวด</div><div><b>ฟรี</b> ทุกบท</div></div>
</section>
<h2 class="home-sec-h">หมวดเวิร์กช็อป</h2>
<p class="home-sec-sub">เลือกหมวดที่ตรงกับงานของคุณ</p>
<div class="mod-grid">{''.join(cards)}</div>
<footer style="border:none">Claude Code Workshops</footer></div></div>
<script src="../assets/app.js"></script></body></html>"""
    open(os.path.join(ROOT, "workshops", "index.html"), "w", encoding="utf-8").write(page)
    print("built workshops/index.html")

if __name__ == "__main__":
    build_workshops()
    build_workshops_index()
    print("done")
