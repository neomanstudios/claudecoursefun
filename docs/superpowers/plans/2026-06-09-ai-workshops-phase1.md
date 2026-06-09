# AI Workshops — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Templatize the approved infographic workshop format into the Python build so workshops render from data, navigate by 7 color-coded categories, and ship 3 hand-written flagship workshops.

**Architecture:** A new `tools/build_workshops.py` (mirroring `build_site.py`/`build_deploy.py`) reads a hand-authored catalog (`data/workshops.json`) and generated content (`data/workshops_content.json`), renders each block type with small pure functions, and writes `workshops/<slug>.html` + `workshops/index.html`. It reuses the existing shared shell helpers and `assets/app.css` (which already contains every component, prototyped on lesson 1.1). The existing Claude Code course is untouched in Phase 1.

**Tech Stack:** Python 3 (stdlib only), the existing static-site build, vanilla CSS in `assets/app.css`, `chrome-devtools` MCP for visual verification. No unit-test framework exists in this repo, so "tests" are a structural-assertion script (`tools/check_workshops.py`) plus screenshots.

---

## Spec reference

Implements Phase 1 of `docs/superpowers/specs/2026-06-09-50-ai-workshops-design.md` (§3 taxonomy, §4 format, §5 data model, §6 build/nav). Phases 2–5 (Claude generator, batch generation, images, course migration) are separate plans.

## File structure

- **Create** `data/workshops.json` — catalog: 7 categories, all 50 workshop titles/goals, `flagship: true` on 3.
- **Create** `data/workshops_content.json` — content blocks for the 3 flagship workshops.
- **Create** `tools/build_workshops.py` — block renderers, sidebar, `render_workshop`, `build_workshops_index`.
- **Create** `tools/check_workshops.py` — structural assertions over generated output.
- **Create** (generated) `workshops/*.html` — written by the build, git-ignored? No: committed like `lessons/*`.
- **Reuse** `assets/app.css`, `assets/app.js`, and from `build_site.py`: `FONTS`, `HEAD_THEME`, `theme_toggle`, `strip_lead_emoji`, `declutter_labels`.

Category → color map (from spec §3): `1 foundations=m4, 2 design=m6, 3 writing=m2, 4 professional=m7, 5 automation=m5, 6 build=m1, 7 learning=m8`.

---

### Task 1: Catalog data (`data/workshops.json`)

**Files:**
- Create: `data/workshops.json`

- [ ] **Step 1: Write the catalog.** Full 7 categories; every workshop has `slug`, `title`, `goal`. Mark 3 flagships. (Slugs are `w-<short>`; keep titles from spec §3. Non-flagship entries render as "coming soon" in nav.)

```json
{
  "categories": [
    { "num": "1", "slug": "foundations", "title": "เริ่มต้นกับ AI", "color": "m4",
      "workshops": [
        { "slug": "w-choose-tool", "title": "เลือกเครื่องมือ AI ให้เหมาะกับงาน", "goal": "เลือกเครื่องมือ AI ได้ถูกกับงานของตัวเอง", "flagship": true },
        { "slug": "w-prompt-basics", "title": "เขียน Prompt ให้ได้ผลลัพธ์ดี", "goal": "เขียน prompt ที่ชัดเจนและได้คำตอบที่ใช้ได้จริง" },
        { "slug": "w-verify-answers", "title": "เช็กความถูกต้องของคำตอบ AI", "goal": "ตรวจสอบและไม่หลงเชื่อคำตอบ AI ที่ผิด" },
        { "slug": "w-ai-safety", "title": "ความปลอดภัยเมื่อใช้ AI", "goal": "ใช้ AI อย่างปลอดภัย ไม่หลุดข้อมูลส่วนตัว" },
        { "slug": "w-setup-accounts", "title": "ตั้งค่าบัญชี AI ยอดนิยม", "goal": "สมัครและตั้งค่า ChatGPT/Claude/Gemini ได้" }
      ] },
    { "num": "2", "slug": "design", "title": "ออกแบบ & ครีเอทีฟ", "color": "m6",
      "workshops": [
        { "slug": "w-logo", "title": "สร้างโลโก้ด้วย AI", "goal": "ได้โลโก้ใช้งานได้จาก AI image gen", "flagship": true },
        { "slug": "w-social-post", "title": "ออกแบบโพสต์โซเชียล", "goal": "ทำภาพโพสต์โซเชียลให้สวยและตรงแบรนด์" },
        { "slug": "w-slides", "title": "ทำสไลด์พรีเซนต์ด้วย AI", "goal": "สร้างสไลด์พรีเซนต์ครบชุดเร็ว ๆ" },
        { "slug": "w-bg-remove", "title": "ลบ/เปลี่ยนพื้นหลังรูป", "goal": "แก้พื้นหลังรูปภาพด้วย AI" },
        { "slug": "w-brand-kit", "title": "สร้าง brand kit", "goal": "ได้ชุดสี ฟอนต์ และสไตล์แบรนด์" },
        { "slug": "w-ui-mockup", "title": "ออกแบบ UI mockup", "goal": "ร่างหน้าตาเว็บ/แอปด้วย AI" },
        { "slug": "w-short-video", "title": "ทำคลิปสั้นด้วย AI", "goal": "สร้างวิดีโอสั้นจากข้อความ/ภาพ" },
        { "slug": "w-sticker-set", "title": "ทำชุดสติกเกอร์/ไอคอน", "goal": "ได้ชุดสติกเกอร์สไตล์เดียวกัน" }
      ] },
    { "num": "3", "slug": "writing", "title": "เขียน & คอนเทนต์", "color": "m2",
      "workshops": [
        { "slug": "w-seo-article", "title": "เขียนบทความ SEO", "goal": "เขียนบทความที่ติดอันดับและอ่านง่าย" },
        { "slug": "w-sales-caption", "title": "เขียนแคปชั่นขายของ", "goal": "เขียนแคปชั่นที่กระตุ้นยอดขาย" },
        { "slug": "w-yt-script", "title": "เขียนสคริปต์ YouTube", "goal": "ได้สคริปต์คลิปที่ลื่นไหล" },
        { "slug": "w-pro-email", "title": "เขียนอีเมลมืออาชีพ", "goal": "ร่างอีเมลงานสุภาพและชัดเจน" },
        { "slug": "w-summarize", "title": "สรุปเอกสารยาว ๆ", "goal": "ย่อเอกสารยาวให้เหลือใจความ" },
        { "slug": "w-translate-tone", "title": "แปล & ปรับโทนภาษา", "goal": "แปลและปรับโทนให้เหมาะกับผู้อ่าน" },
        { "slug": "w-content-plan", "title": "วางแผนคอนเทนต์ 1 เดือน", "goal": "ได้ปฏิทินคอนเทนต์พร้อมไอเดีย" }
      ] },
    { "num": "4", "slug": "professional", "title": "งานอาชีพ & เฉพาะทาง", "color": "m7",
      "workshops": [
        { "slug": "w-resume", "title": "ทำเรซูเม่/CV ให้โดดเด่น", "goal": "ได้เรซูเม่ที่ผ่านด่าน ATS และน่าสนใจ" },
        { "slug": "w-interview-prep", "title": "เตรียมสัมภาษณ์งานกับ AI", "goal": "ซ้อมสัมภาษณ์และตอบได้มั่นใจ" },
        { "slug": "w-excel-analysis", "title": "วิเคราะห์ข้อมูล Excel ด้วย AI", "goal": "วิเคราะห์และสรุปข้อมูลตารางได้" },
        { "slug": "w-market-research", "title": "ทำ market research", "goal": "หาข้อมูลตลาดและคู่แข่งอย่างเป็นระบบ" },
        { "slug": "w-biz-docs", "title": "ร่างเอกสารธุรกิจเบื้องต้น", "goal": "ร่างเอกสาร/ข้อเสนอธุรกิจได้เร็ว" },
        { "slug": "w-personal-finance", "title": "วางแผนการเงินส่วนตัว", "goal": "ทำงบและแผนการเงินด้วยตัวช่วย AI" },
        { "slug": "w-pitch", "title": "ทำ pitch / business plan", "goal": "ได้โครงแผนธุรกิจและสไลด์ pitch" },
        { "slug": "w-sales-assistant", "title": "ผู้ช่วยงานขาย/ตอบลูกค้า", "goal": "ตั้งผู้ช่วยตอบลูกค้าให้เร็วและสุภาพ" }
      ] },
    { "num": "5", "slug": "automation", "title": "ระบบอัตโนมัติ & ผู้ช่วย", "color": "m5",
      "workshops": [
        { "slug": "w-chatbot", "title": "สร้างแชทบอตตอบลูกค้า", "goal": "ได้แชทบอตตอบคำถามพื้นฐานเอง", "flagship": true },
        { "slug": "w-nocode-automation", "title": "automation ด้วย no-code", "goal": "ต่อ AI เข้ากับ Zapier/Make ทำงานอัตโนมัติ" },
        { "slug": "w-personal-assistant", "title": "ตั้งผู้ช่วยส่วนตัว", "goal": "มีผู้ช่วย AI ส่วนตัวช่วยงานประจำวัน" },
        { "slug": "w-rag-docs", "title": "ถามตอบจากเอกสารของเรา", "goal": "ให้ AI ตอบจากไฟล์/เอกสารของเราเอง" },
        { "slug": "w-excel-macro", "title": "ทำสูตร/มาโคร Excel ด้วย AI", "goal": "สร้างสูตรและมาโครจากคำอธิบาย" },
        { "slug": "w-ai-agent", "title": "สร้าง AI agent หลายขั้น", "goal": "ให้ AI ทำงานหลายขั้นตอนต่อเนื่อง" },
        { "slug": "w-mcp-connect", "title": "เชื่อม AI กับเครื่องมือ (MCP)", "goal": "ต่อ AI เข้ากับเครื่องมือที่ใช้อยู่" },
        { "slug": "w-meeting-notes", "title": "ถอดเสียง & สรุปประชุม", "goal": "ได้บันทึกและสรุปการประชุมอัตโนมัติ" }
      ] },
    { "num": "6", "slug": "build", "title": "สร้างแอป & โค้ด", "color": "m1",
      "workshops": [
        { "slug": "w-first-webapp", "title": "สร้างเว็บแอปแรกด้วย Claude Code", "goal": "ได้เว็บแอปง่าย ๆ ที่รันได้จริง" },
        { "slug": "w-debug", "title": "ดีบักด้วย Claude Code", "goal": "หาและแก้บั๊กอย่างเป็นระบบ" },
        { "slug": "w-deploy", "title": "deploy เว็บขึ้นออนไลน์", "goal": "นำเว็บขึ้นออนไลน์ฟรี" },
        { "slug": "w-mcp-db", "title": "เชื่อมฐานข้อมูลผ่าน MCP", "goal": "ให้ Claude อ่าน/เขียนฐานข้อมูล" },
        { "slug": "w-hooks", "title": "ตั้ง hooks อัตโนมัติ", "goal": "ให้ Claude Code ทำงานอัตโนมัติตาม event" },
        { "slug": "w-slash-commands", "title": "สร้าง slash command", "goal": "ทำคำสั่งลัดของตัวเอง" },
        { "slug": "w-multi-agent", "title": "ใช้หลาย agent ทำงานพร้อมกัน", "goal": "แบ่งงานให้หลาย agent ทำขนานกัน" },
        { "slug": "w-headless-ci", "title": "รัน Claude ใน CI/CD", "goal": "ใช้ Claude Code แบบ headless อัตโนมัติ" }
      ] },
    { "num": "7", "slug": "learning", "title": "การศึกษา & เรียนรู้", "color": "m8",
      "workshops": [
        { "slug": "w-tutor", "title": "ติวเตอร์ส่วนตัวด้วย AI", "goal": "มีติวเตอร์ AI อธิบายเรื่องยากให้เข้าใจ" },
        { "slug": "w-flashcards", "title": "ทำ flashcard/quiz จากเนื้อหา", "goal": "สร้างการ์ดคำถามไว้ทบทวน" },
        { "slug": "w-learn-english", "title": "ฝึกภาษาอังกฤษกับ AI", "goal": "ฝึกพูด/เขียนอังกฤษกับ AI" },
        { "slug": "w-lecture-notes", "title": "สรุปเลกเชอร์", "goal": "ย่อเลกเชอร์เป็นโน้ตที่อ่านง่าย" },
        { "slug": "w-research-helper", "title": "ช่วยทำวิจัยอย่างมีจริยธรรม", "goal": "ใช้ AI ช่วยค้นคว้าโดยอ้างอิงถูกต้อง" },
        { "slug": "w-study-plan", "title": "วางแผนการเรียน", "goal": "ได้แผนการเรียนรายสัปดาห์" }
      ] }
  ]
}
```

- [ ] **Step 2: Verify it parses.** Run: `python3 -c "import json; d=json.load(open('data/workshops.json')); print(sum(len(c['workshops']) for c in d['categories']), 'workshops', len(d['categories']), 'categories')"`
  Expected: `50 workshops 7 categories`

- [ ] **Step 3: Commit.** `git add data/workshops.json && git commit -m "Add 50-workshop catalog (7 categories)"`

---

### Task 2: Flagship content (`data/workshops_content.json`)

**Files:**
- Create: `data/workshops_content.json`

Content schema per workshop: `glance{summary,chips[]}`, `blocks[]` (each `{type, heading?, lead?, ...}`), `takeaways[]`, `quiz[]`. Block `type` is one of `compare|concept|keypoint|howto|prompt`. Text fields are trusted HTML (may contain `<b>`,`<code>`). `compare.items[]` = `{name,icon,role,level(1-3),label,color?,best?}`. `concept.items[]` = `{title,body}`. `howto` = `{title,badge,steps[]}`. `prompt` = `{label,text}`.

- [ ] **Step 1: Write all 3 flagships.** Below is the complete `w-choose-tool` (it exercises every block type). Author `w-logo` and `w-chatbot` to the SAME schema with their own content (goals in Task 1; `w-logo` uses a `compare` of image tools + `howto` to produce a logo; `w-chatbot` uses `concept` for how a bot works + `howto` to build one + a `prompt`). All three must include `glance`, at least two distinct block types, one `howto`, one `prompt`, `takeaways`, and a 2-question `quiz`.

```json
{
  "w-choose-tool": {
    "glance": {
      "summary": "เครื่องมือ AI แต่ละตัวเก่งคนละด้าน <b>เลือกตามงาน</b> ไม่ใช่ตามความดัง แล้วงานจะออกมาดีและเร็วขึ้น",
      "chips": ["<b>แชต</b> = ถาม/เขียน", "<b>รูป</b> = ออกแบบ", "<b>โค้ด</b> = สร้างแอป"]
    },
    "blocks": [
      { "type": "compare", "heading": "เลือกตัวไหนดี?", "lead": "จับคู่งานกับเครื่องมือที่ถนัด",
        "items": [
          { "name": "ChatGPT / Claude", "icon": "💬", "role": "ถาม-ตอบ เขียน สรุป วางแผน", "level": 3, "label": "งานข้อความ", "color": "#06B6D4", "best": true },
          { "name": "Midjourney / Nano Banana", "icon": "🎨", "role": "สร้างรูป โลโก้ ภาพประกอบ", "level": 3, "label": "งานภาพ", "color": "#EC4899" },
          { "name": "Claude Code", "icon": "🤖", "role": "สร้างแอป แก้โค้ด อัตโนมัติ", "level": 3, "label": "งานโค้ด", "color": "#F2545B" }
        ] },
      { "type": "keypoint", "text": "ถ้างานเป็น <b>ข้อความ</b> ใช้แชต ถ้าเป็น <b>ภาพ</b> ใช้ image gen ถ้าเป็น <b>โค้ด/แอป</b> ใช้ Claude Code" },
      { "type": "concept", "heading": "3 คำถามก่อนเลือก", "lead": "ตอบ 3 ข้อนี้แล้วจะรู้ทันทีว่าใช้ตัวไหน",
        "items": [
          { "title": "งานออกมาเป็นอะไร?", "body": "ข้อความ ภาพ หรือโปรแกรม ตัวผลลัพธ์บอกเครื่องมือ" },
          { "title": "ต้องแม่นแค่ไหน?", "body": "งานสำคัญใช้ตัวเก่งสุด งานเล่น ๆ ใช้ตัวฟรีก็พอ" },
          { "title": "ต้องต่อกับอะไรไหม?", "body": "ถ้าต้องอ่านไฟล์/ฐานข้อมูล เลือกตัวที่ต่อเครื่องมือได้" }
        ] },
      { "type": "howto", "title": "ลองเลย", "badge": "จับมือทำ",
        "steps": [
          "เขียนงานที่จะทำวันนี้ลงมา 1 อย่าง",
          "ดูว่าผลลัพธ์เป็น ข้อความ/ภาพ/โค้ด",
          "เปิดเครื่องมือที่ตรงกับผลลัพธ์ แล้ววาง prompt ข้างล่าง"
        ] },
      { "type": "prompt", "label": "ลองใช้ Prompt นี้",
        "text": "ฉันอยากได้ [ผลลัพธ์ที่ต้องการ] สำหรับ [งานของฉัน] ช่วยถามกลับ 3 คำถามเพื่อให้เข้าใจงานก่อน แล้วค่อยลงมือทำ" }
    ],
    "takeaways": [
      "เลือกเครื่องมือตามชนิดผลลัพธ์ (ข้อความ/ภาพ/โค้ด)",
      "งานสำคัญใช้ตัวเก่งสุด งานเล่นใช้ตัวฟรี",
      "ถ้าต้องต่อไฟล์/ฐานข้อมูล เลือกตัวที่ต่อเครื่องมือได้"
    ],
    "quiz": [
      { "q": "อยากได้รูปโลโก้ ควรใช้เครื่องมือกลุ่มไหน?", "choices": ["แชตบอตข้อความ", "image generation", "เครื่องมือเขียนโค้ด", "โปรแกรมตารางคำนวณ"], "answer": 1, "explain": "งานภาพให้ใช้กลุ่ม image generation เช่น Midjourney" },
      { "q": "ข้อไหนคือคำถามที่ช่วยเลือกเครื่องมือได้ดีที่สุด?", "choices": ["เครื่องมือไหนดังสุด", "ผลลัพธ์ออกมาเป็นอะไร", "ตัวไหนแพงสุด", "เพื่อนใช้ตัวไหน"], "answer": 1, "explain": "ชนิดของผลลัพธ์ (ข้อความ/ภาพ/โค้ด) เป็นตัวบอกเครื่องมือ" }
    ]
  }
}
```

- [ ] **Step 2: Verify parse + flagship coverage.** Run: `python3 -c "import json; c=json.load(open('data/workshops_content.json')); print(sorted(c)); assert all('glance' in v and 'quiz' in v and any(b['type']=='howto' for b in v['blocks']) for v in c.values()), 'missing required parts'; print('ok')"`
  Expected: lists the 3 slugs then `ok`.

- [ ] **Step 3: Commit.** `git add data/workshops_content.json && git commit -m "Add 3 flagship workshop contents"`

---

### Task 3: Block renderers (`tools/build_workshops.py`)

**Files:**
- Create: `tools/build_workshops.py`

- [ ] **Step 1: Write the module header + block renderers.** Reuse shared helpers from `build_site.py`.

```python
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

# flat list of (category, workshop) and slug->category lookup
FLAT = [(c, w) for c in catalog["categories"] for w in c["workshops"]]
CAT_OF = {w["slug"]: c for c, w in FLAT}

def _sec(heading, lead, sid):
    h = f'<h2 class="sec-title" id="{sid}">{heading}</h2>' if heading else ""
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
            f'<div class="prompt-text" id="pt">{html.escape(b["text"])}</div>'
            f'<button class="copy-btn" onclick="cp()">คัดลอก Prompt</button></div>')

RENDERERS = {"compare": block_compare, "concept": block_concept,
             "keypoint": block_keypoint, "howto": block_howto, "prompt": block_prompt}

def render_blocks(blocks):
    """Return (html, toc_items). Blocks with a heading/howto get a TOC id."""
    out, toc = "", []
    for i, b in enumerate(blocks, 1):
        sid = f"sec-{i}"
        out += RENDERERS[b["type"]](b, sid)
        if b.get("heading"):
            toc.append((sid, b["heading"]))
        elif b["type"] == "howto":
            toc.append((sid, b.get("title", "ลองเลย")))
    return out, toc
```

- [ ] **Step 2: Smoke-test the renderers.** Run:
```bash
python3 -c "import sys; sys.path.insert(0,'tools'); import build_workshops as b; c=b.content['w-choose-tool']; h,toc=b.render_blocks(c['blocks']); assert 'vs-grid' in h and 'howto' in h and 'concept-grid' in h; print('blocks ok, toc:', [t[1] for t in toc])"
```
  Expected: `blocks ok, toc: ['เลือกตัวไหนดี?', '3 คำถามก่อนเลือก', 'ลองเลย']`

- [ ] **Step 3: Commit.** `git add tools/build_workshops.py && git commit -m "Add workshop block renderers"`

---

### Task 4: Sidebar + workshop page renderer

**Files:**
- Modify: `tools/build_workshops.py`

- [ ] **Step 1: Add `ws_sidebar`, `ws_quiz`, `ws_takeaways`, `render_workshop`, `build_workshops`.** Append to the module.

```python
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
            '<span class="sb-brand">AI Workshops<small>เรียนใช้ AI ทำงานจริง</small></span></a>'
            f'{theme_toggle()}</div>'
            f'<nav class="sb-nav">{"".join(rows)}</nav>'
            '<div class="sb-back"><a href="../index.html">← คอร์ส Claude Code</a></div></aside>')

def render_workshop(cat, w):
    c = content[w["slug"]]
    body, toc = render_blocks(c["blocks"])
    body = declutter_labels(body)
    toc_links = "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t in toc)
    toc_links += '<a href="#quiz" class="toc-quiz">แบบทดสอบ</a>'
    img = f'../images/{w["slug"]}.webp'
    fig = (f'<figure class="lesson-hero"><img src="{img}" alt="{html.escape(w["title"])}" '
           f'loading="lazy" decoding="async"></figure>') if os.path.exists(
           os.path.join(ROOT, "images", w["slug"] + ".webp")) else ""
    return f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(w["title"])} | AI Workshops</title>
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
<footer>AI Workshops · เรียนใช้ AI ทำงานจริง</footer></div>
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
```

- [ ] **Step 2: Add the `.sb-soon` style** so "coming soon" items read as muted (append to `assets/app.css`).

```css
/* coming-soon workshop (no page yet) */
.sb-soon{display:flex;align-items:center;gap:.5rem;padding:.42rem .55rem;font-size:.83rem;
  color:var(--muted);opacity:.7}
.sb-soon em{margin-left:auto;font-style:normal;font-size:.66rem;font-weight:700;color:var(--muted);
  background:var(--bg-2);border-radius:99px;padding:.1rem .5rem}
```

- [ ] **Step 3: Build + assert pages exist.** Run:
```bash
python3 -c "import sys; sys.path.insert(0,'tools'); import build_workshops as b; b.build_workshops()"
test -f workshops/w-choose-tool.html && grep -q 'class="glance"' workshops/w-choose-tool.html && echo PAGE_OK
```
  Expected: `built 3 workshop pages` then `PAGE_OK`.

- [ ] **Step 4: Commit.** `git add tools/build_workshops.py assets/app.css workshops/ && git commit -m "Render workshop pages with category sidebar"`

---

### Task 5: Workshops landing (`workshops/index.html`)

**Files:**
- Modify: `tools/build_workshops.py`

- [ ] **Step 1: Add `build_workshops_index` and a `__main__` block.**

```python
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
<title>AI Workshops | เรียนใช้ AI ทำงานจริง</title>
<meta name="description" content="50 เวิร์กช็อปลงมือทำ เรียนใช้ AI กับงานจริง">
{HEAD_THEME}{FONTS}<link rel="stylesheet" href="../assets/app.css"></head>
<body data-slug="__wshome__">
<div class="reading-bar" id="bar"></div><div class="sb-overlay"></div>
{ws_sidebar(None)}
<div class="main"><div class="topbar"><button class="hamb" id="hamb" aria-label="เมนู">☰</button>
<span class="tb-title">AI Workshops</span>{theme_toggle()}</div>
<div class="home"><section class="home-hero">
<span class="tag">ลงมือทำได้จริง</span>
<h1>เรียนใช้ AI ทำงานจริง</h1>
<p>{total} เวิร์กช็อปสั้น ๆ จับมือทำทีละขั้น ตั้งแต่ออกแบบ เขียน งานอาชีพ ระบบอัตโนมัติ ไปจนถึงสร้างแอป</p>
<div class="home-stats"><div><b>{total}</b> เวิร์กช็อป</div><div><b>{len(catalog['categories'])}</b> หมวด</div><div><b>ฟรี</b> ทุกบท</div></div>
</section>
<h2 class="home-sec-h">หมวดเวิร์กช็อป</h2>
<p class="home-sec-sub">เลือกหมวดที่ตรงกับงานของคุณ</p>
<div class="mod-grid">{''.join(cards)}</div>
<footer style="border:none">AI Workshops · เรียนใช้ AI ทำงานจริง</footer></div></div>
<script src="../assets/app.js"></script></body></html>"""
    open(os.path.join(ROOT, "workshops", "index.html"), "w", encoding="utf-8").write(page)
    print("built workshops/index.html")

if __name__ == "__main__":
    build_workshops()
    build_workshops_index()
    print("done")
```

- [ ] **Step 2: Run full build.** Run: `python3 tools/build_workshops.py`
  Expected: `built 3 workshop pages` / `built workshops/index.html` / `done`.

- [ ] **Step 3: Commit.** `git add tools/build_workshops.py workshops/ && git commit -m "Add workshops landing page"`

---

### Task 6: Structural checks + visual verification

**Files:**
- Create: `tools/check_workshops.py`

- [ ] **Step 1: Write the check script.**

```python
#!/usr/bin/env python3
"""Structural assertions over generated workshop output. Exit non-zero on failure."""
import os, sys, json, glob
ROOT = os.path.join(os.path.dirname(__file__), "..")
content = json.load(open(os.path.join(ROOT, "data", "workshops_content.json"), encoding="utf-8"))

def check():
    idx = os.path.join(ROOT, "workshops", "index.html")
    assert os.path.exists(idx), "missing workshops/index.html"
    home = open(idx, encoding="utf-8").read()
    assert home.count('class="mod-card') == 7, "landing must show 7 category cards"
    for slug in content:
        p = os.path.join(ROOT, "workshops", slug + ".html")
        assert os.path.exists(p), f"missing page {slug}"
        h = open(p, encoding="utf-8").read()
        for need in ('class="glance"', 'id="quiz"', 'data-mod=', 'app.css'):
            assert need in h, f"{slug} missing {need}"
        assert "var(--p)" not in h and "var(--teal)" not in h, f"{slug} has legacy tokens"
    print(f"OK: index + {len(content)} workshop pages pass structural checks")

if __name__ == "__main__":
    try:
        check()
    except AssertionError as e:
        print("FAIL:", e); sys.exit(1)
```

- [ ] **Step 2: Run it.** Run: `python3 tools/check_workshops.py`
  Expected: `OK: index + 3 workshop pages pass structural checks`

- [ ] **Step 3: Visual check.** Start/confirm preview (`.claude/launch.json` → `static-site` on :8765), then screenshot in the browser (chrome-devtools MCP), light + dark:
  - `http://localhost:8765/workshops/index.html`
  - `http://localhost:8765/workshops/w-choose-tool.html`
  Confirm: 7 colored category cards on the landing; the workshop shows glance band, comparison meter, concept cards, hands-on steps, prompt, quiz; dark mode clean; coming-soon items muted.

- [ ] **Step 4: Commit.** `git add tools/check_workshops.py && git commit -m "Add workshop structural checks"`

---

## Self-Review

- **Spec coverage:** §3 taxonomy → Task 1 (all 50, 7 cats, colors). §4 format → Tasks 3-4 (every block type rendered; matches lesson-1.1 prototype). §5 data model → Tasks 1-2 (`workshops.json` + `workshops_content.json`, exact schema). §6 build/nav → Tasks 4-5 (`render_workshop`, category sidebar, landing) + reuse of `app.css`/`app.js`/shared helpers. Authoring (§7) and images (§4) are Phase 2+ — out of this plan by design.
- **Placeholder scan:** No TBDs in code. `w-logo`/`w-chatbot` content is authored editorial work in Task 2 Step 1 against a fully-specified schema + a complete worked example (`w-choose-tool`); their goals are fixed in Task 1.
- **Type consistency:** `content` keys = workshop `slug`; `cat["color"]` is `"mN"`, sliced `[1:]` → `data-mod="N"` consistently in sidebar, page body, and index cards. `RENDERERS` keys match block `type` values used in Task 2. `render_blocks` returns `(html, toc)` used by `render_workshop`.

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-09-ai-workshops-phase1.md`.** Phases 2–5 (Claude `gen_workshop.py` generator, batch generation, Gemini images for workshops, migrate the Claude Code course into Category 6) will each get their own plan.
