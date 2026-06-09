#!/usr/bin/env python3
"""สร้างหน้าเว็บใหม่ทั้งหมดเป็นธีม e-learning (light + sidebar)
- regenerate ทุกบทใน lessons/ จาก data/course.json + data/meta.json
- สร้าง index.html (หน้าหลักคอร์ส) ใหม่
- เนื้อหาเดิม (block/prompt/note/takeaways) ถูกนำกลับมาใช้ พร้อมโครงสร้างใหม่
ใช้คู่กับ assets/app.css และ assets/app.js
"""
import os, re, json, html
from gen_images import LESSONS as IMG_CAPS, DEPLOY as IMG_DEPLOY

ROOT = os.path.join(os.path.dirname(__file__), "..")
course = json.load(open(os.path.join(ROOT,"data","course.json"),encoding="utf-8"))
meta = json.load(open(os.path.join(ROOT,"data","meta.json"),encoding="utf-8")) if \
       os.path.exists(os.path.join(ROOT,"data","meta.json")) else {}
detail = json.load(open(os.path.join(ROOT,"data","detail.json"),encoding="utf-8")) if \
       os.path.exists(os.path.join(ROOT,"data","detail.json")) else {}

def detail_body(slug, orig_body):
    """ถ้ามีเนื้อหาขยาย (detail.json) ใช้ blocks ใหม่แทน .block เดิม
    แต่คง prompt-box / note / takeaways เดิมไว้ (ส่วนท้าย)"""
    d = detail.get(slug)
    if not d or not d.get("blocks"):
        return orig_body
    blocks = ""
    for b in d["blocks"]:
        inner = "".join(f"<p>{p}</p>" for p in b.get("p",[]) if p.strip())
        steps = [s for s in b.get("steps",[]) if s.strip()]
        if steps:
            inner += '<ol class="steps">' + "".join(f"<li>{s}</li>" for s in steps) + '</ol>'
        h_text = re.sub(r'<[^>]+>', '', b.get("h",""))  # headings เป็นข้อความล้วน (ตัด tag เช่น <code>)
        blocks += f'<div class="block"><h3>{html.escape(h_text)}</h3>{inner}</div>'
        if b.get("note","").strip():
            blocks += (f'<div class="note"><span class="ni">💡</span>'
                       f'<div class="note-body">{b["note"]}</div></div>')
    # คงส่วนท้ายเดิม (prompt-box / note / takeaways) ไว้
    idxs = [orig_body.find(m) for m in ('<div class="prompt-box">','<div class="note">','<div class="takeaways">')]
    idxs = [i for i in idxs if i >= 0]
    tail = orig_body[min(idxs):] if idxs else ""
    return blocks + tail
CAPS = {**IMG_CAPS, **IMG_DEPLOY}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@500;600;700&'
 'family=Sarabun:wght@400;500;600;700;800&'
 'family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">')

# Anti-FOUC theme script: set data-theme before paint + flag JS on for scroll-reveal.
HEAD_THEME = ('<script>(function(){try{var t=localStorage.getItem("cc_theme");'
 'if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}'
 'document.documentElement.className+=" js";})();</script>')

def theme_toggle():
    return ('<button class="theme-toggle" type="button" aria-label="สลับโหมดสว่าง/มืด" '
            'title="สลับโหมดสว่าง/มืด">🌙</button>')

def strip_lead_emoji(s):
    """Drop a leading decorative emoji/symbol (+ spaces) from a title.
    Keeps Latin/Thai/alnum; modules are identified by color + number now."""
    s = s.lstrip()
    while s and ord(s[0]) > 0x2000 and not ('฀' <= s[0] <= '๿'):
        s = s[1:]
    return s.lstrip()

def declutter_labels(h):
    """Remove repetitive decorative emoji from generated lesson body HTML
    (prompt label, takeaways title, copy button, note icon)."""
    h = re.sub(r'(<div class="prompt-label">)\s*💬\s*', r'\1', h)
    h = re.sub(r'(<div class="tk-title">)\s*📌\s*', r'\1', h)
    h = re.sub(r'(<button class="copy-btn"[^>]*>)\s*📋\s*', r'\1', h)
    h = h.replace('<span class="ni">💡</span>', '')
    return h

def rel(href, from_lessons):
    """แปลง href ที่อ้างอิงจาก root ให้ถูกต้องตามตำแหน่งไฟล์"""
    if from_lessons:
        if href.startswith("lessons/"): return href[len("lessons/"):]
        return "../" + href            # deploy.html, index.html
    return href                         # already root-relative

def sidebar(active_slug, from_lessons):
    home = "../index.html" if from_lessons else "index.html"
    asset = "../assets/" if from_lessons else "assets/"
    rows = []
    for mod in course["modules"]:
        active_in = any(l["slug"]==active_slug for l in mod["lessons"])
        op = " open" if active_in else ""
        lis = []
        for l in mod["lessons"]:
            cls = " active" if l["slug"]==active_slug else ""
            href = rel(l["href"], from_lessons)
            lis.append(
              f'<li><a href="{href}" data-slug="{l["slug"]}" class="{cls.strip()}">'
              f'<span class="dot"></span><span class="ln">{l["num"]}</span>'
              f'<span>{html.escape(l["title"])}</span></a></li>')
        rows.append(
          f'<details class="sb-mod" data-mod="{mod["num"]}"{op}><summary>'
          f'<span class="mn">{mod["num"]}</span>'
          f'<span class="mt">{html.escape(strip_lead_emoji(mod["title"]))}</span>'
          f'<span class="mk">▶</span></summary>'
          f'<ul class="sb-les">{"".join(lis)}</ul></details>')
    return (
    '<aside class="sidebar">'
      '<div class="sb-head">'
        f'<a href="{home}" class="sb-brand-link">'
          '<span class="sb-logo">⚡</span>'
          '<span class="sb-brand">Claude Code Hub<small>คอร์สเรียนภาษาไทย</small></span></a>'
        f'{theme_toggle()}</div>'
      '<div class="sb-progress"><div class="lbl"><span>ความคืบหน้า</span><b>0/0 บท</b></div>'
        '<div class="sb-bar"><i></i></div></div>'
      f'<nav class="sb-nav">{"".join(rows)}</nav>'
      f'<div class="sb-back"><a href="{home}">← หน้าหลักคอร์ส</a></div>'
    '</aside>')

def figure(slug, from_lessons):
    img = ("../images/" if from_lessons else "images/") + slug + ".webp"
    cap = CAPS.get(slug, ("",""))[1]
    if not os.path.exists(os.path.join(ROOT,"images",slug+".webp")):
        return ""
    return (f'<figure class="lesson-hero"><img src="{img}" alt="{html.escape(cap)}" '
            f'loading="lazy" decoding="async">'
            f'<figcaption>{html.escape(cap)}</figcaption></figure>')

def objectives_html(slug):
    m = meta.get(slug)
    if not m or not m.get("objectives"): return ""
    items = "".join(f"<li>{html.escape(o)}</li>" for o in m["objectives"])
    return ('<div class="objectives"><h2>เมื่อเรียนจบบทนี้ คุณจะ…</h2>'
            f'<ul>{items}</ul></div>')

def quiz_html(slug):
    m = meta.get(slug)
    if not m or not m.get("quiz"): return ""
    qs = []
    for i,q in enumerate(m["quiz"],1):
        choices = []
        letters = "ABCD"
        for j,c in enumerate(q["choices"]):
            choices.append(
              f'<button class="choice"><span class="mk">{letters[j]}</span>'
              f'<span>{html.escape(c)}</span></button>')
        qs.append(
          f'<div class="q" data-answer="{q["answer"]}">'
          f'<div class="q-text"><span class="qn">ข้อ {i}.</span>{html.escape(q["q"])}</div>'
          f'<div class="choices">{"".join(choices)}</div>'
          f'<div class="q-explain"><strong>เฉลย:</strong> {html.escape(q.get("explain",""))}</div>'
          '</div>')
    return ('<div class="quiz" id="quiz"><div class="quiz-h">แบบทดสอบท้ายบท</div>'
            '<div class="quiz-sub">ลองตอบดู แล้วระบบจะเฉลยให้ทันที</div>'
            f'{"".join(qs)}</div>')

def pagenav(les, from_lessons):
    def btn(href, title, nxt):
        if not href:
            d = "ถัดไป →" if nxt else "← ก่อนหน้า"
            empty = "นี่คือบทสุดท้าย" if nxt else "นี่คือบทแรก"
            return f'<span class="pn-btn disabled {"pn-next" if nxt else ""}"><span class="pn-dir">{d}</span><span class="pn-title">{empty}</span></span>'
        cls = "pn-next" if nxt else ""
        d = "ถัดไป →" if nxt else "← ก่อนหน้า"
        return (f'<a href="{rel(href,from_lessons)}" class="pn-btn {cls}">'
                f'<span class="pn-dir">{d}</span><span class="pn-title">{html.escape(title or "")}</span></a>')
    return ('<div class="pagenav">'
            + btn(les.get("prev"), les.get("prev_title"), False)
            + btn(les.get("next"), les.get("next_title"), True) + '</div>')

def add_section_ids(body_html):
    """ใส่ id ให้หัวข้อ <h3> ในแต่ละ .block และคืนรายการสำหรับสารบัญด้านขวา"""
    items = []
    counter = [0]
    def repl(m):
        counter[0]+= 1
        sid = f"sec-{counter[0]}"
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        items.append((sid, html.unescape(text)))
        return f'<div class="block"><h3 id="{sid}">{m.group(1)}</h3>'
    new = re.sub(r'<div class="block"><h3>(.*?)</h3>', repl, body_html, flags=re.S)
    return new, items

def toc_html(items, has_quiz):
    if not items and not has_quiz: return ""
    links = "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid,t in items)
    if has_quiz:
        links += '<a href="#quiz" class="toc-quiz">แบบทดสอบท้ายบท</a>'
    return f'<aside class="toc"><div class="toc-t">ในบทนี้</div>{links}</aside>'

def render_lesson(les):
    c = les["content"]; slug = les["slug"]
    title = c.get("h1") or les["title"]
    body_with_ids, toc_items = add_section_ids(declutter_labels(detail_body(slug, c.get('body_html',''))))
    page = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} | Claude Code Hub</title>
<meta name="description" content="{html.escape(c.get('intro','')[:150])}">
{HEAD_THEME}
{FONTS}
<link rel="stylesheet" href="../assets/app.css">
</head>
<body data-slug="{slug}" data-mod="{html.escape(les['module_num'])}">
<div class="reading-bar" id="bar"></div>
<div class="sb-overlay"></div>
{sidebar(slug, True)}
<div class="main">
  <div class="topbar"><button class="hamb" id="hamb" aria-label="เมนู">☰</button>
    <span class="tb-title">{html.escape(les['module_num'])}. {html.escape(strip_lead_emoji(les['module_title']))}</span>
    {theme_toggle()}</div>
  <div class="docs">
    <article class="reading">
      <div class="crumb"><a href="../index.html">หน้าหลัก</a> › โมดูล {html.escape(les['module_num'])}: {html.escape(strip_lead_emoji(les['module_title']))}</div>
      <span class="les-no">บทเรียน {html.escape(c.get('lesson_no','').replace('บทเรียน','').strip() or les['num'])}</span>
      <h1>{html.escape(title)}</h1>
      <p class="lead">{html.escape(c.get('intro',''))}</p>
      {objectives_html(slug)}
      {figure(slug, True)}
      {body_with_ids}
      {quiz_html(slug)}
      <div class="complete-row"><button class="btn-complete" id="btnComplete">✓ ทำเครื่องหมายว่าเรียนจบ</button></div>
      {pagenav(les, True)}
    </article>
    {toc_html(toc_items, bool(meta.get(slug,{}).get('quiz')))}
  </div>
  <footer>Claude Code Learning Hub · เรียนฟรี · Curated by <strong>Chetaphong Preecha</strong> &amp; Beyond Team</footer>
</div>
<script src="../assets/app.js"></script>
</body>
</html>"""
    return page

def build_lessons():
    n = 0
    for mod in course["modules"]:
        for les in mod["lessons"]:
            if les["slug"] == "deploy":   # special page, handled separately
                continue
            path = os.path.join(ROOT, les["href"])
            if not les.get("content",{}).get("body_html"):
                print("  ! no body for", les["slug"], "- skip"); continue
            open(path,"w",encoding="utf-8").write(render_lesson(les))
            n += 1
    print(f"built {n} lesson pages")

def build_index():
    cards = []
    for mod in course["modules"]:
        lis = []
        for l in mod["lessons"]:
            lis.append(f'<li><a href="{l["href"]}" data-slug="{l["slug"]}">'
                       f'<span class="dot"></span><span class="ln">{l["num"]}</span>'
                       f'<span>{html.escape(l["title"])}</span></a></li>')
        cards.append(
          f'<section class="mod-card reveal" data-mod="{mod["num"]}">'
          f'<div class="mc-head"><span class="mn">{mod["num"]}</span>'
          f'<div><h3>{html.escape(strip_lead_emoji(mod["title"]))}</h3>'
          f'<p>{html.escape(mod["sub"])}</p></div>'
          f'<span class="mc-count">{len(mod["lessons"])} บท</span></div>'
          f'<ul class="mc-list">{"".join(lis)}</ul></section>')

    # "what you'll learn" highlights (color-coded)
    feats = [
      ("1","🚀","เริ่มจากศูนย์ได้จริง","ไม่ต้องมีพื้นฐานเขียนโปรแกรม คอร์สพาไปทีละขั้นจนสร้างเว็บแอปด้วย AI ได้เอง"),
      ("4","💬","ลงมือทำตามทันที","ทุกบทมีตัวอย่าง prompt ที่ก๊อปไปใช้ได้เลย พร้อมภาพประกอบเข้าใจง่าย"),
      ("5","🎯","รู้ว่าเรียนถึงไหน","แบบทดสอบท้ายบทเฉลยทันที และระบบติดตามความคืบหน้าบันทึกให้อัตโนมัติ"),
    ]
    learn = "".join(
      f'<div class="learn-card reveal" data-mod="{m}">'
      f'<div class="ic">{ic}</div><h4>{html.escape(t)}</h4><p>{html.escape(d)}</p></div>'
      for m,ic,t,d in feats)

    first = course["modules"][0]["lessons"][0]["href"]
    total = course.get("total", sum(len(m["lessons"]) for m in course["modules"]))
    page = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code Learning Hub | คอร์สเรียนภาษาไทย</title>
<meta name="description" content="คอร์สเรียน Claude Code ภาษาไทย สำหรับมือใหม่ เรียนฟรี มีภาพประกอบ แบบทดสอบ และติดตามความคืบหน้าได้">
{HEAD_THEME}
{FONTS}
<link rel="stylesheet" href="assets/app.css">
</head>
<body data-slug="__home__">
<div class="reading-bar" id="bar"></div>
<div class="sb-overlay"></div>
{sidebar(None, False)}
<div class="main">
  <div class="topbar"><button class="hamb" id="hamb" aria-label="เมนู">☰</button>
    <span class="tb-title">Claude Code Hub</span>
    {theme_toggle()}</div>
  <div class="home">
    <section class="home-hero">
      <span class="tag">เรียนฟรี · มือใหม่ทำตามได้</span>
      <h1>เรียน Claude Code สร้างเว็บแอปด้วย AI</h1>
      <p>คอร์สภาษาไทยที่พามือใหม่ไม่มีพื้นฐาน ใช้ Claude Code สร้างงานจริงได้ทีละขั้น
         มีภาพประกอบทุกบท แบบทดสอบท้ายบท และติดตามความคืบหน้าได้</p>
      <a href="{first}" class="home-cta">เริ่มเรียนบทแรก →</a>
      <div class="home-stats">
        <div><b>{total}</b> บทเรียน</div>
        <div><b>{len(course['modules'])}</b> โมดูล</div>
        <div><b>ฟรี</b> ทุกบท</div>
      </div>
    </section>

    <div class="learn-grid">{learn}</div>

    <h2 class="home-sec-h">เนื้อหาคอร์ส</h2>
    <p class="home-sec-sub">{len(course['modules'])} โมดูล · {total} บทเรียน · แต่ละโมดูลมีสีของตัวเองให้จำง่าย</p>
    <div class="mod-grid">{''.join(cards)}</div>

    <footer style="border:none">Claude Code Learning Hub · Curated by <strong>Chetaphong Preecha</strong> &amp; Beyond Team</footer>
  </div>
</div>
<script src="assets/app.js"></script>
</body>
</html>"""
    open(os.path.join(ROOT,"index.html"),"w",encoding="utf-8").write(page)
    print("built index.html")

if __name__ == "__main__":
    build_lessons()
    build_index()
    print("done")
