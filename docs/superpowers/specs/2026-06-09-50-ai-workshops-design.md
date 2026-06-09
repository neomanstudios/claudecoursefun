# Design Spec — 50 Hands-On AI Workshops (AI-Skills Platform)

**Date:** 2026-06-09
**Status:** Draft for review
**Builds on:** the existing static course (Python build → `assets/app.css` + `lessons/*.html`) and the new infographic lesson format prototyped on lesson 1.1.

---

## 1. Goal

Grow the project from a single Claude Code course into a **broad, beginner-friendly AI-skills platform**: **50 hands-on workshops** that teach people to *use AI for real tasks* — design, writing, professional work, automation, building software, and studying. Thai-language, Gen-Z-friendly, scannable (infographics over text walls), each ending in something the learner actually did.

### Success criteria
- 50 workshops live, each in the infographic format (essence band → visual blocks → hands-on steps → prompt → quiz).
- Organized into 7 color-coded categories; sidebar + landing navigate by category.
- Content authored by **Claude** (Anthropic API) into a structured schema; per-workshop illustration via the existing Gemini image pipeline.
- Static site, no backend (progress stays in `localStorage`); deterministic Python build.

---

## 2. Scope (decided)

- **Broad AI-skills platform.** The current Claude Code course becomes **one category among seven**, not the whole product.
- Net-new: 50 workshops. The existing Claude Code lessons are **reframed** into Category 6 (see §3); they are not thrown away.
- Out of scope for this spec: accounts/login, a real "share" backend, the sticker-book/badges feature (separate spec), payments.

---

## 3. Taxonomy (decided — 7 categories, 50 workshops)

| # | Category (TH / EN) | Color | Count | Example workshops |
|---|---|---|:--:|---|
| 1 | เริ่มต้นกับ AI / Foundations | `--m4` cyan | 5 | เลือกเครื่องมือให้เหมาะกับงาน · เขียน prompt พื้นฐาน · เช็กความถูกต้องของคำตอบ · ความปลอดภัยในการใช้ AI · ตั้งค่าบัญชี AI |
| 2 | ออกแบบ & ครีเอทีฟ / Design | `--m6` pink | 8 | โลโก้ · โพสต์โซเชียล · สไลด์พรีเซนต์ · ลบ/เปลี่ยนพื้นหลังรูป · brand kit · UI mockup · คลิปสั้น · ชุดสติกเกอร์ |
| 3 | เขียน & คอนเทนต์ / Writing | `--m2` amber | 7 | บทความ SEO · แคปชั่นขายของ · สคริปต์ YouTube · อีเมลมืออาชีพ · สรุปเอกสารยาว · แปล & ปรับโทน · โพสต์โซเชียล |
| 4 | งานอาชีพ & เฉพาะทาง / Professional | `--m7` indigo | 8 | เรซูเม่/CV · เตรียมสัมภาษณ์ · วิเคราะห์ข้อมูล Excel · market research · ร่างเอกสารธุรกิจ · วางแผนการเงิน · business plan · ผู้ช่วยงานขาย |
| 5 | ระบบอัตโนมัติ & ผู้ช่วย / Automation + Q&A | `--m5` green | 8 | แชทบอตตอบลูกค้า · automation no-code · ผู้ช่วยส่วนตัว · ถามตอบจากเอกสารของเรา · สูตร/มาโคร Excel · AI agent หลายขั้น · เชื่อม AI กับเครื่องมือ (MCP) · ถอดเสียง/สรุปประชุม |
| 6 | สร้างแอป & โค้ด / Build with Claude Code | `--m1` coral | 8 | reframed from the existing 8-module Claude Code course as workshop-projects (build a web app, debug, deploy, MCP, hooks, multi-agent, …) |
| 7 | การศึกษา & เรียนรู้ / Learning | `--m8` teal | 6 | ติวเตอร์ส่วนตัว · flashcard/quiz จากเนื้อหา · ฝึกภาษาอังกฤษ · สรุปเลกเชอร์ · ช่วยทำวิจัยอย่างมีจริยธรรม · วางแผนการเรียน |

**Total = 50.** Final per-workshop titles are enumerated in the implementation plan; the counts above are fixed.

---

## 4. Workshop format (decided — prototyped on lesson 1.1)

Every workshop renders these blocks (all already styled in `assets/app.css`):

1. **Glance** (`.glance`) — "รู้ใน 30 วิ": 1–2 sentence essence + 3 chips. The *เนื้อ* up top.
2. **Hero image** (`figure.lesson-hero`) — bright, per-category-colored illustration (Gemini).
3. **Visual blocks** — one or more of:
   - **Comparison** (`.vs-grid` + autonomy/level meter) — for "X vs Y vs Z".
   - **Concept cards** (`.concept-grid`, numbered) — replaces bullet walls.
   - **Key-point** (`.keypoint`) — the one thing to remember.
4. **Hands-on** (`.howto`, "ลองเลย / จับมือทำ") — numbered, tactile steps.
5. **Prompt** (`.prompt-box`) — a copyable prompt the learner runs.
6. **Takeaways** (`.takeaways`) — checklist recap.
7. **Quiz** (`.quiz`) — 2–3 questions, instant answers.

Emoji: minimal ("พอดี") — only meaningful category/comparison icons. Dark mode + reduced-motion supported by the shared CSS.

---

## 5. Data model

Two data files (extending today's `data/` pattern):

- **`data/workshops.json`** — the *catalog* (hand-maintained):
  ```json
  {
    "categories": [
      { "num": "1", "slug": "foundations", "title": "เริ่มต้นกับ AI", "color": "m4",
        "workshops": [ { "slug": "w-choose-tool", "title": "เลือกเครื่องมือ AI ให้เหมาะกับงาน",
                         "goal": "ผู้เรียนเลือกเครื่องมือ AI ได้ถูกกับงานของตัวเอง", "level": "beginner" } ] }
    ]
  }
  ```
- **`data/workshops_content.json`** — the *generated content* (by the Claude script), keyed by workshop slug, matching the block schema:
  ```json
  { "w-choose-tool": {
      "glance": { "summary": "…", "chips": ["…","…","…"] },
      "blocks": [
        { "type": "compare", "items": [ { "name":"ChatGPT", "icon":"💬", "role":"…", "level":2 } ] },
        { "type": "concept", "items": [ { "title":"…", "body":"…" } ] },
        { "type": "keypoint", "text": "…" },
        { "type": "howto", "title":"ลองเลย", "badge":"จับมือทำ", "steps":[ "…","…","…" ] },
        { "type": "prompt", "label":"ลองใช้ Prompt นี้", "text":"…" }
      ],
      "takeaways": ["…","…","…"],
      "quiz": [ { "q":"…", "choices":["…"], "answer":1, "explain":"…" } ]
  } }
  ```

Catalog is authored by a human (titles/goals are product decisions); content blocks are generated and reviewed.

---

## 6. Build & navigation

Extend `tools/build_site.py`:
- **`render_workshop(ws, content)`** — emits the §4 block HTML from `workshops_content.json` (a small renderer per block `type`). This *templatizes* the lesson-1.1 prototype.
- **Sidebar + landing** reorganize by the 7 categories (reusing the `data-mod`/`--mc` color system; categories map to `m1…m8`). Landing shows 7 category cards + counts.
- Output: `workshops/<slug>.html`, same shell (sidebar, TOC, progress, quiz) as today.
- Progress tracking (`localStorage`) and the dark-mode toggle work unchanged.
- The existing `lessons/*.html` (Claude Code course) remain and are surfaced under Category 6; migrating them into `render_workshop` is a later step, not a blocker.

---

## 7. Authoring pipeline (decided — Claude writes the content, in-session)

There is **no Anthropic API key available**, so workshops are authored by **Claude directly in the working session** (this assistant), not by an API script:
- Work from the `data/workshops.json` catalog (category, title, goal).
- Claude writes each workshop's content into `data/workshops_content.json` following the exact block schema (§5): Thai, Gen-Z-friendly, scannable, minimal emoji, a runnable prompt, 2–3 quiz items, **no em-dashes**.
- Authored in **batches by category**, reviewed (spec + quality) before the build renders them. The 3 flagships set the quality bar.
- The build (`build_workshops.py`) renders only workshops that have content; the rest show "เร็ว ๆ นี้" until authored.
- No `gen_workshop.py` / no `ANTHROPIC_API_KEY` needed. (If an Anthropic key becomes available later, this could be scripted, but it is not required.)

**Images:** per-workshop illustrations continue via `tools/gen_images.py` (Gemini), reusing the per-category color in the prompt builder. (Claude cannot generate images.)

---

## 8. Phasing (for the implementation plan)

1. **Templatize the format** — move the lesson-1.1 prototype into `render_workshop`; add `workshops.json` + `workshops_content.json` plumbing; restyle landing/sidebar by category. Ship with 2–3 **hand-written flagship** workshops (one validates each block type).
2. **Author content in batches** — Claude writes the remaining workshops into `workshops_content.json` one category at a time (in-session), reviewing each batch; the build renders them as they land.
3. **Generate the rest** — batch the remaining workshops, review, publish.
4. **Images** — extend the Gemini image map to the 50 workshops; generate.
5. **Migrate** the existing Claude Code lessons into Category 6's workshop format.

Each phase is independently shippable and reviewable.

---

## 9. Open decisions (defaults chosen; flag to change)

- **Existing course:** stays live; becomes Category 6; reformatting into `render_workshop` is Phase 5 (not blocking). *Default: keep, migrate later.*
- **URL layout:** new pages under `workshops/<slug>.html`; existing `lessons/*` kept for now (no broken links). *Default: additive, no breaking renames.*
- **Generation model tier:** capable model for flagships, faster tier for bulk. *Default: tune for cost during Phase 2.*
- **Catalog titles:** the 50 exact titles are finalized in the implementation plan from the examples in §3.

---

## 10. Non-goals (separate specs)

- Sticker-book badges + shareable progress "port" page.
- Accounts, payments, a sharing backend.
