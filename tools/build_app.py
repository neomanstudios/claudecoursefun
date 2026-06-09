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

# deploy (lesson 8.3) is hand-authored HTML (data/.. has no body_html); its content
# lives in ROOT/deploy.html with bespoke components. Render a DARK version so the
# sidebar link doesn't 404. We map the light component tokens to the dark palette.
_DEPLOY_ALIAS = """
:root{--ink:var(--text);--ink-2:var(--text-2);--mc:var(--accent-2);--radius:14px;
  --shadow:0 18px 40px -26px rgba(0,0,0,.8);--shadow-sm:0 10px 24px -20px rgba(0,0,0,.7);
  --ok-soft:rgba(52,211,153,.14);--ok-ink:#34D399;--accent-soft:rgba(59,130,246,.18);
  --bad-soft:rgba(248,113,113,.12);--font-display:var(--font)}
"""
_DEPLOY_OVERRIDE = """
.container{max-width:none;margin:0;padding:0}
.hl{background:linear-gradient(135deg,var(--mc),var(--accent-2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hl2{color:var(--mc)}
.sec-head{margin:2.2rem 0 1rem}
.sec-tag{display:inline-block;font-family:var(--mono);font-size:.74rem;font-weight:700;color:var(--mc);background:color-mix(in srgb,var(--mc) 14%,transparent);padding:.2rem .7rem;border-radius:20px;margin-bottom:.5rem}
.sec-head h2{font-weight:800;font-size:1.5rem;margin-bottom:.3rem;color:var(--ink)}
.sec-head p{color:var(--muted);font-size:.95rem}
.intro-box{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1.3rem;margin-bottom:1.4rem;box-shadow:var(--shadow-sm)}
.intro-box h3{font-weight:700;font-size:1.15rem;margin-bottom:.6rem;color:var(--ink)}
.intro-box p{color:var(--ink-2);margin-bottom:.6rem}
.quick-nav{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.4rem}
.qn-link{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.5rem .9rem;font-size:.85rem;font-weight:600;color:var(--ink-2);transition:.15s}
.qn-link:hover{border-color:var(--mc);color:var(--mc)}
.compare{overflow-x:auto;margin-bottom:1.4rem}
.compare table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;font-size:.9rem}
.compare th{background:var(--bg-2);text-align:left;padding:.7rem .9rem;font-weight:700;color:var(--ink);border-bottom:1px solid var(--line)}
.compare td{padding:.7rem .9rem;border-bottom:1px solid var(--line-2);color:var(--ink-2)}
.compare tr:last-child td{border-bottom:none}
.badge-best{display:inline-block;background:var(--ok-soft);color:var(--ok-ink);font-size:.7rem;font-weight:700;padding:.1rem .5rem;border-radius:20px;margin-left:.3rem}
.platform{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1.4rem;margin-bottom:1.4rem;box-shadow:var(--shadow-sm)}
.plat-head{display:flex;gap:.9rem;align-items:flex-start;margin-bottom:.9rem}
.plat-logo{width:46px;height:46px;border-radius:13px;background:color-mix(in srgb,var(--mc) 15%,transparent);display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0}
.plat-name{font-weight:700;font-size:1.15rem;color:var(--ink)}
.plat-tagline{color:var(--muted);font-size:.86rem;margin:.15rem 0 .4rem}
.plat-tags{display:flex;flex-wrap:wrap;gap:.4rem}
.ptag{font-size:.72rem;font-weight:700;padding:.18rem .55rem;border-radius:20px}
.ptag-free{background:var(--ok-soft);color:var(--ok-ink)}
.ptag-fast{background:var(--accent-soft);color:var(--accent-2)}
.ptag-easy{background:color-mix(in srgb,var(--accent-2) 16%,transparent);color:var(--accent-2)}
.plat-best{background:var(--bg-2);border-left:3px solid var(--mc);border-radius:8px;padding:.7rem .9rem;font-size:.88rem;color:var(--ink-2);margin-bottom:1rem}
.plat-best strong{color:var(--ink)}
.way{border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;margin-bottom:1rem}
.way-easy{background:color-mix(in srgb,var(--mc) 9%,var(--card));border-color:color-mix(in srgb,var(--mc) 26%,var(--line))}
.way-manual{background:var(--bg-2)}
.way-title{font-weight:700;font-size:.98rem;margin-bottom:.6rem;color:var(--ink)}
.action-list{list-style:none;margin:.3rem 0;padding:0}
.action-list li{display:flex;gap:.7rem;align-items:flex-start;margin-bottom:.6rem}
.action-num{width:24px;height:24px;border-radius:50%;background:var(--mc);color:#04140C;font-weight:800;font-size:.78rem;font-family:var(--mono);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.action-text{color:var(--ink-2);font-size:.92rem;line-height:1.65}
.action-text strong{color:var(--ink)}
.action-text small{display:block;color:var(--muted);font-size:.8rem;margin-top:.2rem}
.result-url{display:flex;gap:.6rem;align-items:center;background:var(--ok-soft);border:1px solid color-mix(in srgb,var(--ok) 40%,transparent);border-radius:10px;padding:.7rem .9rem;margin-top:.8rem;color:var(--ok-ink);font-size:.9rem}
.result-url .ri{font-size:1.2rem}
.terminal{background:#060912;border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:.6rem 0}
.term-bar{display:flex;align-items:center;gap:.4rem;padding:.5rem .8rem;background:rgba(255,255,255,.03)}
.tdot{width:11px;height:11px;border-radius:50%}
.term-title{color:var(--text-2);font-size:.78rem;margin-left:.4rem;font-family:var(--mono)}
.term-body{padding:.8rem 1rem;font-family:var(--mono);font-size:.84rem;color:#E7E9F3;white-space:pre-wrap;line-height:1.7}
.prompt{color:#7CFFB2}.cmd{color:#E7E9F3}.cmt{color:#8b93a7}.ok{color:#7CFFB2}
.copy-cmd{background:var(--grad-cta);color:#fff;border:none;border-radius:8px;padding:.35rem .8rem;font-size:.78rem;font-weight:700;font-family:var(--font);cursor:pointer;margin-top:-.2rem}
.domain-box{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1.4rem;margin-bottom:1.4rem;box-shadow:var(--shadow-sm)}
.note-warn{background:var(--bad-soft);border:1px solid color-mix(in srgb,var(--bad) 35%,transparent);border-left:4px solid var(--bad)}
.note-tip{background:color-mix(in srgb,var(--accent-2) 12%,var(--card));border:1px solid color-mix(in srgb,var(--accent-2) 30%,var(--line));border-left:4px solid var(--accent-2)}
.next-section{margin-top:2rem}
.next-box{background:linear-gradient(135deg,color-mix(in srgb,var(--mc) 14%,var(--card)),color-mix(in srgb,var(--accent-2) 12%,var(--card)));border:1px solid color-mix(in srgb,var(--mc) 26%,var(--line));border-radius:18px;padding:2rem;text-align:center}
.next-box .mt{font-weight:800;font-size:1.2rem;color:var(--ink);margin-bottom:.4rem;display:block}
.next-box p{color:var(--ink-2)}
.go-btn{display:inline-flex;align-items:center;gap:.4rem;background:var(--grad-cta);color:#fff;font-weight:700;padding:.7rem 1.4rem;border-radius:12px}
.go-link{display:inline-flex;align-items:center;gap:.4rem;background:var(--card);border:1px solid var(--line);color:var(--text);font-weight:700;padding:.7rem 1.4rem;border-radius:12px}
.fade-up{opacity:1}
"""

def build_deploy():
    src = open(os.path.join(ROOT, "deploy.html"), encoding="utf-8").read()
    body = src[src.index('<div class="container">'):src.index('<footer>')].strip()
    body = re.sub(r'<figure class="lesson-hero".*?</figure>', '', body, flags=re.S)
    body = declutter_labels(body)
    les = next(l for l in FLAT if l["slug"] == "deploy")
    i = FLAT.index(les)
    prev = FLAT[i-1] if i > 0 else None
    if prev:
        ph = (prev["href"][len("lessons/"):] if prev["href"].startswith("lessons/") else prev["href"])
        prev_b = f'<a class="pn-a" href="{ph}"><span class="d">&#8592; บทก่อนหน้า</span><span class="t">{html.escape(prev["title"])}</span></a>'
    else:
        prev_b = '<span class="pn-a disabled"><span class="d">&#8592; บทก่อนหน้า</span><span class="t">นี่คือบทแรก</span></span>'
    next_b = '<span class="pn-a nx disabled"><span class="d">จบคอร์ส &#127881;</span><span class="t">คุณเรียนครบแล้ว!</span></span>'
    toc = ('<a href="#cloudflare">Cloudflare Pages</a><a href="#vercel">Vercel</a>'
           '<a href="#github">GitHub Pages</a><a href="#netlify">Netlify</a><a href="#domain">โดเมนของตัวเอง</a>')
    page = f"""<!DOCTYPE html>
<html lang="th">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Deploy เว็บขึ้นออนไลน์ | Claude Code</title>
<meta name="description" content="เอาเว็บขึ้นออนไลน์ฟรี ด้วย Cloudflare Pages, Vercel, GitHub Pages หรือ Netlify ทำตามทีละขั้น">
<script>(function(){{try{{var t=localStorage.getItem('cc_app_theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}document.documentElement.className+=' js';}})();</script>
{FONTS}<link rel="stylesheet" href="../app.css">
<style>{_DEPLOY_ALIAS}{_DEPLOY_OVERRIDE}</style></head>
<body data-slug="deploy">
<div class="sb-overlay"></div>
{outline("deploy")}
<div class="shell">
{topbar()}
<div class="content">
<div class="main">
<div class="crumb"><a class="back" href="../index.html"><svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="m15 18-6-6 6-6"/></svg>หน้าหลัก</a><span class="sep">&#8250;</span>โมดูล 8: Workshop สร้าง Portfolio Website<span class="sep">&#8250;</span>บทเรียน 8.3</div>
<div class="les-head"><div><h1>เอาเว็บขึ้นออนไลน์ ให้คนทั้งโลกเห็น</h1><p>เว็บที่รันบนเครื่องคุณ พร้อมแชร์แล้ว เลือกแพลตฟอร์มที่ชอบแล้วทำตามทีละขั้น หรือให้ Claude Code ช่วย deploy ก็ได้ ทุกแพลตฟอร์มมีแพลนฟรี</p></div>
<div class="ring"><svg viewBox="0 0 36 36"><circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="3.4"/><circle class="ring-i" cx="18" cy="18" r="15.5" fill="none" stroke="url(#rg)" stroke-width="3.4" stroke-linecap="round" stroke-dasharray="0 100" transform="rotate(-90 18 18)"/><text class="ring-t" x="18" y="21" text-anchor="middle" font-size="8.5" font-weight="800" fill="#EAEEF9" font-family="Plus Jakarta Sans">0%</text><defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3B82F6"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient></defs></svg><div class="rlbl">ความคืบหน้าคอร์ส</div></div></div>
{cover(les, "deploy")}
<div class="ov"><div class="ov-main">{body}
<div class="complete-row"><button class="btn-complete" id="btnComplete">ทำเครื่องหมายว่าเรียนจบ</button></div></div>
<aside class="ov-side"><div class="card toc"><div class="toc-t">ในบทนี้</div>{toc}</div></aside></div>
<div class="pn">{prev_b}{next_b}</div>
</div>
</div></div>
<script>function copyText(id,btn){{var t=document.getElementById(id).innerText;navigator.clipboard.writeText(t).then(function(){{var o=btn.innerHTML;btn.innerHTML='คัดลอกแล้ว';btn.classList.add('done');setTimeout(function(){{btn.innerHTML=o;btn.classList.remove('done')}},1600)}});}}</script>
<script src="../app.js"></script></body></html>"""
    open(os.path.join(OUT, "deploy.html"), "w", encoding="utf-8").write(page)
    print("built app/lessons/deploy.html (dark)")

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
    build_deploy()
    build_index()
    print(f"built {n} dark lesson pages")
