#!/usr/bin/env python3
"""Generate the dark "AI Online" LMS lesson player for every Claude Code lesson.
Reuses the content generators from build_site (detail_body / objectives / quiz),
wraps them in the dark player shell, and writes app/lessons/<slug>.html + app/index.html.
Uses app/app.css + app/app.js (the dark design system)."""
import os, re, html, json
from build_site import (course, meta, detail_body, objectives_html, quiz_html,
                        add_section_ids, declutter_labels)

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "app", "lessons")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&'
 'family=Sarabun:wght@400;500;600;700&display=swap" rel="stylesheet">')

# flat lesson order for prev/next + progress
FLAT = [l for m in course["modules"] for l in m["lessons"]]
TOTAL = len(FLAT)


def topbar():
    return ('<header class="topbar"><button class="hamb" aria-label="เมนู"><svg class="ic" viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>'
      '<span class="tb-here">เนื้อหาบทเรียน</span></header>')

def outline(active_slug):
    """Dark course outline sidebar: modules -> lessons."""
    rows = []
    for mod in course["modules"]:
        op = " open" if any(l["slug"] == active_slug for l in mod["lessons"]) else ""
        lis = []
        for l in mod["lessons"]:
            cls = " active" if l["slug"] == active_slug else ""
            href = (l["href"][len("lessons/"):] if l["href"].startswith("lessons/") else l["href"]).replace(".html", ".html")
            lis.append(f'<li><a href="{href}" data-slug="{l["slug"]}" class="{cls.strip()}">'
                       f'<span class="dot"></span><span class="ln">{l["num"]}</span>'
                       f'<span class="lt">{html.escape(l["title"])}</span></a></li>')
        rows.append(f'<details class="mod"{op}><summary><span class="mn">{mod["num"]}</span>'
                    f'<span class="mt">{html.escape(strip_emoji(mod["title"]))}</span>'
                    f'<svg class="chev ic" viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"/></svg></summary>'
                    f'<ul class="lessons">{"".join(lis)}</ul></details>')
    return ('<aside class="sidebar"><div class="brand"><a href="../index.html" class="brand-l">'
            '<span class="logo">CC</span><b>Claude Code</b></a></div>'
            '<div class="sb-switch"><a href="../index.html" class="active">บทเรียน</a>'
            '<a href="../workshops/index.html">เวิร์กช็อป</a></div>'
            '<div class="sb-progress"><div class="pl"><span>ความคืบหน้า</span><b class="prog-lbl">0/0</b></div>'
            '<div class="pbar"><i></i></div></div>'
            f'<div class="sb-scroll">{"".join(rows)}</div>'
            '<a class="sb-back" href="../index.html"><svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="m15 18-6-6 6-6"/></svg>หน้าหลักคอร์ส</a></aside>')

def strip_emoji(s):
    s = s.lstrip()
    while s and ord(s[0]) > 0x2000 and not ('฀' <= s[0] <= '๿'):
        s = s[1:]
    return s.lstrip()

def cover(les, slug):
    img = f"../../images/{slug}.webp"
    has_img = os.path.exists(os.path.join(ROOT, "images", slug + ".webp"))
    style = f'style="background-image:linear-gradient(90deg,rgba(8,11,22,.92),rgba(8,11,22,.35)),url(\'{img}\')"' if has_img else ""
    return (f'<div class="cover" {style}>'
            f'<div class="ctxt"><div class="k">{html.escape(les["module_num"])}.{les["num"].split(".")[-1] if "." in les["num"] else les["num"]} · {html.escape(strip_emoji(les["module_title"]))}</div>'
            f'<h2>{html.escape(les["content"].get("h1") or les["title"])}</h2></div>'
            f'<span class="readbadge"><svg class="ic" viewBox="0 0 24 24" style="width:14px;color:var(--accent-2)"><path d="M4 19V6a2 2 0 0 1 2-2h7v17H6a2 2 0 0 1-2-2Z"/><path d="M13 4h5a2 2 0 0 1 2 2v13"/></svg>บทเรียนแบบอ่าน</span></div>')


# --- turn raw step lists into clean, structured steps for the guided stepper ---
# Source steps (detail.json) are inconsistent: some carry literal "1." / "ขั้นที่ 2:"
# prefixes (duplicating the visible number), unrendered **bold**, and a prompt buried
# inline as <code> or "quoted text". We normalise each step and lift the prompt into
# an inline copy-tray so every step is self-contained and focused.
_LEAD_ENUM = re.compile(
    r'^\s*(?:\d+\s*[.)\:]\s*'
    r'|ขั้น(?:ตอน)?ที่\s*\d+\s*[:：.)]?\s*'
    r'|STEP\s*\d+\s*[:：.)]?\s*)', re.IGNORECASE)
_BOLD = re.compile(r'\*\*(.+?)\*\*', re.S)
_CODE = re.compile(r'<code>(.*?)</code>', re.S)
_QUOTE = re.compile(r'[\"“]([^\"”]{25,})[\"”]')
_TITLE = re.compile(r'^\s*<strong>(.*?)</strong>\s*[:：]?\s*(.*)$', re.S)
_PROMPT_SVG = ('<svg class="ic" viewBox="0 0 24 24" style="width:15px">'
    '<path d="M9 9h9a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2Z"/>'
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>')
_CMD_SVG = ('<svg class="ic" viewBox="0 0 24 24" style="width:15px">'
    '<path d="m6 8 4 4-4 4"/><path d="M13 16h5"/></svg>')

def prompt_tray(prompt):
    """An inline copy-tray for a prompt/command. Thai text -> 'Prompt'; ASCII -> 'คำสั่ง' (mono).
    Reused by lesson steps and workshop howto steps."""
    ptxt = re.sub(r'<[^>]+>', '', prompt)
    is_thai = any('฀' <= ch <= '๿' for ch in ptxt)
    icon, label, cls = (_PROMPT_SVG, 'พิมพ์ Prompt นี้', 'sp-text') if is_thai \
                       else (_CMD_SVG, 'คัดลอกคำสั่งนี้', 'sp-text sp-cmd')
    return (f'<div class="step-prompt"><div class="sp-top">{icon}{label}</div>'
            f'<code class="{cls}">{prompt}</code>'
            f'<button class="sp-copy" type="button">{_PROMPT_SVG}คัดลอก</button></div>')

def _one_step(s):
    s = _LEAD_ENUM.sub('', s.strip())
    s = _BOLD.sub(r'<strong>\1</strong>', s).replace('**', '')
    prompt = None
    m = _CODE.search(s)
    if m and len(re.sub(r'<[^>]+>', '', m.group(1)).strip()) >= 25:
        prompt = m.group(1).strip(); s = s[:m.start()] + s[m.end():]
    else:
        m = _QUOTE.search(s)
        if m:
            prompt = m.group(1).strip(); s = s[:m.start()] + s[m.end():]
    s = re.sub(r'[\s:：\-–—"“”]+$', '', s).strip()
    title, desc = None, s
    mt = _TITLE.match(s)
    if mt:
        title = mt.group(1).strip().rstrip(':：').strip(); desc = mt.group(2).strip()
    main = ''
    if title: main += f'<div class="st-t">{title}</div>'
    if desc:  main += f'<div class="st-d">{desc}</div>'
    if prompt:
        main += prompt_tray(prompt)
    return f'<li class="step"><div class="st-main">{main}</div></li>'

def restructure_steps(body):
    def repl(m):
        lis = re.findall(r'<li>(.*?)</li>', m.group(1), re.S)
        if not lis: return m.group(0)
        attr = ' data-stepper' if len(lis) >= 2 else ''
        return f'<ol class="steps"{attr}>' + ''.join(_one_step(li) for li in lis) + '</ol>'
    return re.sub(r'<ol class="steps">(.*?)</ol>', repl, body, flags=re.S)

def render(les):
    c = les["content"]; slug = les["slug"]
    title = c.get("h1") or les["title"]
    body, toc_items = add_section_ids(declutter_labels(restructure_steps(detail_body(slug, c.get("body_html", "")))))
    obj = objectives_html(slug)
    qz = quiz_html(slug)
    toc = "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t in toc_items)
    # prev / next
    i = next((k for k, l in enumerate(FLAT) if l["slug"] == slug), 0)
    def navbtn(idx, nxt):
        if idx < 0 or idx >= TOTAL: return ""
        l = FLAT[idx]
        href = (l["href"][len("lessons/"):] if l["href"].startswith("lessons/") else l["href"])
        d = "บทถัดไป &#8594;" if nxt else "&#8592; บทก่อนหน้า"
        cls = "pn-a nx" if nxt else "pn-a"
        return f'<a class="{cls}" href="{href}"><span class="d">{d}</span><span class="t">{html.escape(l["title"])}</span></a>'
    prev_b = navbtn(i-1, False) or '<span class="pn-a disabled"><span class="d">&#8592; บทก่อนหน้า</span><span class="t">นี่คือบทแรก</span></span>'
    next_b = navbtn(i+1, True) or '<span class="pn-a nx disabled"><span class="d">บทถัดไป &#8594;</span><span class="t">จบคอร์ส</span></span>'
    tabs = ('<div class="tabs"><button class="on" data-tab="overview">ภาพรวม</button>'
            + ('<button data-tab="quiz">แบบทดสอบ</button>' if qz else '') + '</div>')
    quiz_panel = f'<section class="tab-panel" data-panel="quiz" hidden>{qz}</section>' if qz else ''
    return f"""<!DOCTYPE html>
<html lang="th">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} | Claude Code</title>
<meta name="description" content="{html.escape(c.get('intro','')[:150])}">
<script>(function(){{try{{var t=localStorage.getItem('cc_app_theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}document.documentElement.className+=' js';}})();</script>
{FONTS}<link rel="stylesheet" href="../app.css"></head>
<body data-slug="{slug}">
<div class="sb-overlay"></div>
{outline(slug)}
<div class="shell">
{topbar()}
<div class="content">
<div class="main">
<div class="crumb"><a class="back" href="../index.html"><svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="m15 18-6-6 6-6"/></svg>หน้าหลัก</a><span class="sep">&#8250;</span>โมดูล {html.escape(les['module_num'])}: {html.escape(strip_emoji(les['module_title']))}<span class="sep">&#8250;</span>บทเรียน {html.escape(les['num'])}</div>
<div class="les-head"><div><h1>{html.escape(title)}</h1><p>{html.escape(c.get('intro',''))}</p></div>
<div class="ring"><svg viewBox="0 0 36 36"><circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="3.4"/><circle class="ring-i" cx="18" cy="18" r="15.5" fill="none" stroke="url(#rg)" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="0 100" transform="rotate(-90 18 18)"/><text class="ring-t" x="18" y="21" text-anchor="middle" font-size="8.5" font-weight="800" fill="#EAEEF9" font-family="Plus Jakarta Sans">0%</text><defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3B82F6"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient></defs></svg><div class="rlbl">ความคืบหน้าคอร์ส</div></div></div>
{cover(les, slug)}
{tabs}
<section class="tab-panel" data-panel="overview">
<div class="ov"><div class="ov-main">{obj}{body}
<div class="complete-row"><button class="btn-complete" id="btnComplete">ทำเครื่องหมายว่าเรียนจบ</button></div></div>
<aside class="ov-side">{f'<div class="card toc"><div class="toc-t">ในบทนี้</div>{toc}{"<a href=#quiz class=tq>แบบทดสอบ</a>" if qz else ""}</div>' if toc else ''}</aside></div>
</section>
{quiz_panel}
<div class="pn">{prev_b}{next_b}</div>
</div>
</div></div>
<script src="../app.js"></script></body></html>"""

def build_index():
    cards = []
    for mod in course["modules"]:
        lis = []
        for l in mod["lessons"]:
            href = "lessons/" + (l["href"][len("lessons/"):] if l["href"].startswith("lessons/") else l["href"])
            lis.append(f'<li><a href="{href}" data-slug="{l["slug"]}"><span class="dot"></span>'
                       f'<span class="ln">{l["num"]}</span><span>{html.escape(l["title"])}</span></a></li>')
        cards.append(f'<section class="mcard" data-mod="{mod["num"]}"><div class="mc-h"><span class="mn">{mod["num"]}</span>'
                     f'<div><h3>{html.escape(strip_emoji(mod["title"]))}</h3><p>{html.escape(mod.get("sub",""))}</p></div>'
                     f'<span class="cnt">{len(mod["lessons"])} บท</span></div><ul class="lessons mc-list">{"".join(lis)}</ul></section>')
    first = FLAT[0]["href"][len("lessons/"):] if FLAT[0]["href"].startswith("lessons/") else FLAT[0]["href"]
    total = course.get("total", TOTAL)
    page = f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code | คอร์สเรียนภาษาไทย</title>
<script>(function(){{try{{var t=localStorage.getItem('cc_app_theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}document.documentElement.className+=' js';}})();</script>
{FONTS}<link rel="stylesheet" href="app.css"></head>
<body data-slug="__home__">
<div class="sb-overlay"></div>
{outline(None).replace('href="../workshops/index.html"','href="workshops/index.html"').replace('href="../index.html"','href="index.html"').replace('../../workshops','../workshops').replace('href="01','href="lessons/01').replace('href="02','href="lessons/02').replace('href="03','href="lessons/03').replace('href="04','href="lessons/04').replace('href="05','href="lessons/05').replace('href="06','href="lessons/06').replace('href="07','href="lessons/07').replace('href="08','href="lessons/08').replace('href="deploy','href="lessons/deploy')}
<div class="shell">
{topbar().replace('href="../','href="')}
<div class="home">
<div class="hero"><div class="k">คอร์สเรียนภาษาไทย</div><h1>เรียนใช้ <em>Claude Code</em> สร้างงานจริง</h1>
<p>{total} บทเรียน · {len(course['modules'])} โมดูล · เรียนฟรีทุกบท พามือใหม่ใช้ AI agent สร้างงานได้ทีละขั้น</p>
<div class="hero-cta"><a class="cta" href="lessons/{first}">เริ่มเรียนบทแรก &#8594;</a>
<a class="cta2" href="workshops/index.html">เวิร์กช็อปลงมือทำ 50 แบบ &#8594;</a></div></div>
<h2 class="sec">เนื้อหาคอร์ส</h2>
<div class="mgrid">{''.join(cards)}</div>
</div></div>
<script src="app.js"></script></body></html>"""
    open(os.path.join(ROOT, "app", "index.html"), "w", encoding="utf-8").write(page)
    print("built app/index.html")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for les in FLAT:
        if not les.get("content", {}).get("body_html"):
            continue
        slug = les["slug"]
        fn = (les["href"][len("lessons/"):] if les["href"].startswith("lessons/") else les["href"])
        open(os.path.join(OUT, os.path.basename(fn)), "w", encoding="utf-8").write(render(les))
        n += 1
    build_index()
    print(f"built {n} dark lesson pages")
