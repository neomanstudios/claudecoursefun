#!/usr/bin/env python3
"""Generate the dark "AI Online" LMS lesson player for every Claude Code lesson.
Reuses the content generators from build_site (detail_body / objectives / quiz),
wraps them in the dark player shell, and writes app/lessons/<slug>.html + app/index.html.
Uses app/app.css + app/app.js (the dark design system)."""
import os, html, json
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

NAV = ('<nav class="nav">'
  '<a href="../index.html"><svg class="ic" viewBox="0 0 24 24"><path d="M3 9.5 12 3l9 6.5V20a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/></svg>หน้าหลัก</a>'
  '<a href="../index.html" class="active"><svg class="ic" viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h6v18H6a2 2 0 0 1-2-2Z"/><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"/></svg>การเรียนของฉัน</a>'
  '<a href="../../workshops/index.html"><svg class="ic" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>เวิร์กช็อป</a>'
  '</nav>')

def topbar():
    return ('<header class="topbar"><button class="hamb" aria-label="เมนู"><svg class="ic" viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>'
      '<div class="search"><svg class="ic" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3-3"/></svg>'
      '<input placeholder="ค้นหาบทเรียน หัวข้อ..."></div>'
      '<div class="tb-right">'
      '<button class="icon-btn" aria-label="แจ้งเตือน"><span class="dot"></span><svg class="ic" viewBox="0 0 24 24"><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg></button>'
      '<button class="icon-btn" aria-label="ความสำเร็จ"><svg class="ic" viewBox="0 0 24 24"><path d="M6 4h12v3a6 6 0 0 1-12 0Z"/><path d="M6 5H3v2a3 3 0 0 0 3 3M18 5h3v2a3 3 0 0 1-3 3M9 17h6M10 21h4M12 13v4"/></svg></button>'
      '<div class="profile"><span class="av-c">CC</span><div><div class="nm">ผู้เรียน</div><div class="rl">Claude Code Course</div></div></div></div></header>')

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

def rail(les, slug):
    title = html.escape(les["content"].get("h1") or les["title"])
    return ('<aside class="rail">'
      '<div class="assist"><h3><svg class="ic" viewBox="0 0 24 24" style="stroke:var(--accent-2)"><path d="m12 3 2.2 5.6L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.8-.4Z"/></svg>ผู้ช่วย AI</h3>'
      '<p class="sub">ถามอะไรเกี่ยวกับบทเรียนนี้ได้เลย</p>'
      '<button class="chip"><span class="ico"><svg class="ic" viewBox="0 0 24 24" style="width:14px"><path d="M12 3a9 9 0 1 0 9 9"/><path d="M12 7v5"/></svg></span>อธิบายบทนี้แบบง่าย ๆ</button>'
      '<button class="chip"><span class="ico"><svg class="ic" viewBox="0 0 24 24" style="width:14px"><rect x="4" y="4" width="16" height="16" rx="2"/></svg></span>ขอตัวอย่างการใช้งานจริง</button>'
      '<button class="chip"><span class="ico"><svg class="ic" viewBox="0 0 24 24" style="width:14px"><path d="m5 12 5 5 9-11"/></svg></span>ทดสอบความเข้าใจของฉัน</button>'
      '<button class="ask"><svg class="ic" viewBox="0 0 24 24" style="width:16px;stroke:#fff"><path d="m12 3 2.2 5.6L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.8-.4Z"/></svg>ถามผู้ช่วย AI</button></div>'
      '<div class="card"><div class="rc-head"><h3>โน้ตของฉัน</h3><a href="#">+ เพิ่มโน้ต</a></div>'
      '<div class="note-e"><textarea placeholder="จดสิ่งที่อยากจำจากบทนี้..."></textarea></div></div>'
      '<div class="card"><div class="rc-head"><h3>พูดคุย</h3><a href="#">ดูทั้งหมด</a></div>'
      f'<div class="disc"><span class="av">ปอ</span><div><div class="nm">ปอ ศิริพร <span class="tm">2 ชม.</span></div>'
      f'<div class="q">ขอบคุณครับ บทนี้เข้าใจง่ายดี!</div><div class="meta"><span>ตอบกลับ</span><span>&#9825; 8</span></div></div></div></div>'
      '</aside>')

def render(les):
    c = les["content"]; slug = les["slug"]
    title = c.get("h1") or les["title"]
    body, toc_items = add_section_ids(declutter_labels(detail_body(slug, c.get("body_html", ""))))
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
{rail(les, slug)}
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
{outline(None).replace('class="active"','').replace('href="../index.html"','href="index.html"').replace('../../workshops','../workshops').replace('href="01','href="lessons/01').replace('href="02','href="lessons/02').replace('href="03','href="lessons/03').replace('href="04','href="lessons/04').replace('href="05','href="lessons/05').replace('href="06','href="lessons/06').replace('href="07','href="lessons/07').replace('href="08','href="lessons/08').replace('href="deploy','href="lessons/deploy')}
<div class="shell">
{topbar().replace('href="../','href="')}
<div class="home">
<div class="hero"><div class="k">คอร์สเรียนภาษาไทย</div><h1>เรียนใช้ <em>Claude Code</em> สร้างงานจริง</h1>
<p>{total} บทเรียน · {len(course['modules'])} โมดูล · เรียนฟรีทุกบท พามือใหม่ใช้ AI agent สร้างงานได้ทีละขั้น</p>
<a class="cta" href="lessons/{first}">เริ่มเรียนบทแรก &#8594;</a></div>
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
