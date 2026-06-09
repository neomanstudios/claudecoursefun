#!/usr/bin/env python3
"""สร้างภาพประกอบบทเรียนด้วย Gemini 2.5 Flash Image (Gemini 2)
- ภาพละ 1 ไฟล์ .webp ในโฟลเดอร์ images/
- โทนสีสดใส หลากสี ตามธีมเว็บใหม่ โดยแต่ละภาพเน้นสีประจำโมดูลของตัวเอง
- ข้ามไฟล์ที่มีอยู่แล้ว เพื่อให้รันซ้ำได้ (resume); ใส่ --force เพื่อสร้างใหม่ทั้งหมด
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from io import BytesIO

# NOTE: PIL and the API key (GEMINI_API_KEY / GEMINI_KEY) are only needed for
# actual image generation. They are imported/read lazily inside gen()/save_webp()
# so that other tools (e.g. build_site.py) can import the LESSONS/DEPLOY caption
# dicts below without Pillow installed or an API key set.
MODEL = "gemini-2.5-flash-image"
OUT = os.path.join(os.path.dirname(__file__), "..", "images")
FORCE = "--force" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]

BASE = ("Bright, cheerful, modern flat vector illustration for a beginner-friendly AI coding course. "
        "Playful rounded shapes, smooth flat color fills, soft light shadows, clean and generous negative space, "
        "friendly and approachable, crisp and high quality, centered balanced composition. "
        "No text, no words, no letters, no numbers, no captions, no realistic UI screenshots. ")

# Each module owns a color (matches assets/app.css --m1..--m8). Every lesson's
# illustration leans into its module color so the art reinforces the same
# wayfinding palette as the rest of the site.
MODULE_ACCENT = {
 "1":("coral","#F2545B"), "2":("amber","#F59E0B"), "3":("violet","#8B5CF6"),
 "4":("cyan","#06B6D4"),  "5":("green","#22C55E"), "6":("pink","#EC4899"),
 "7":("indigo","#6366F1"),"8":("teal","#14B8A6"),
}

def module_of(slug):
    """Map a lesson slug to its module number (deploy = module 8)."""
    if slug == "deploy":
        return "8"
    head = slug.split("-", 1)[0].lstrip("0")
    return head or "8"

def build_prompt(slug, subject):
    name, hexv = MODULE_ACCENT.get(module_of(slug), ("blue", "#3361FF"))
    return (BASE
            + f"Soft pastel {name}-tinted background. "
            + f"Dominant accent color {name} ({hexv}), with bright supporting pops of "
              "coral, amber, violet, cyan, green, pink, indigo and teal. "
            + "Subject: " + subject)

# slug -> (english subject for the image, thai caption shown under image)
LESSONS = {
 "01-what-is-claude-code": ("Three side-by-side panels comparing AI coding helpers: a small inline autocomplete suggestion popup, a code editor window with an AI chat bubble, and a friendly robot working inside a terminal window — showing escalating autonomy from left to right.",
    "Copilot เติมโค้ดทีละบรรทัด · Cursor คือ editor ฝัง AI · Claude Code คือ agent ที่ทำงานเองในเทอร์มินัล"),
 "01-agentic-mode": ("A friendly robot inside a terminal window following a loop: read files, edit code, run tests, repeat — shown as a circular arrow workflow with small file and checkmark icons.",
    "Agentic mode = อ่านไฟล์ → แก้โค้ด → รันเทส → วนซ้ำเองจนงานเสร็จ"),
 "01-real-use-cases": ("A toolbox opening to reveal real developer tasks as glowing icons: bug fixing, building a feature, writing tests, refactoring, and documentation.",
    "ตัวอย่างงานจริงที่ Claude Code ช่วยได้: แก้บั๊ก สร้างฟีเจอร์ เขียนเทส รีแฟคเตอร์"),
 "01-limitations": ("A friendly robot beside a caution sign and a fenced boundary, indicating limits and things to double-check, calm and reassuring tone.",
    "รู้ขอบเขตและข้อจำกัด เพื่อใช้งานอย่างปลอดภัยและได้ผล"),
 "02-install": ("A laptop showing a terminal with a download/install progress and a VS Code-like editor icon, plus a plug connecting them, clean setup scene.",
    "ติดตั้ง Claude Code CLI และส่วนขยายใน editor"),
 "02-api-key": ("A glowing key entering a secure lock on a login card with a small billing/credit-card icon, secure and trustworthy mood.",
    "ล็อกอินและตั้งค่าการเรียกเก็บเงินอย่างปลอดภัย"),
 "02-claude-md": ("A document file labeled with a memo icon acting as a project guidebook, with a robot reading it to understand the project context.",
    "CLAUDE.md = คู่มือโปรเจกต์ที่ Claude อ่านก่อนเริ่มทำงาน"),
 "02-settings": ("A settings gear opening a panel of toggles and sliders that adjust a robot's behavior, configuration dashboard style.",
    "settings.json ปรับพฤติกรรมและค่าเริ่มต้นของ Claude Code"),
 "02-permissions": ("A shield with allow/deny checkmarks guarding tools (file, terminal, network) that a robot may use, security gate concept.",
    "ระบบ Permission ควบคุมว่า Claude ทำอะไรได้บ้าง"),
 "03-context-first": ("A robot receiving a well-organized briefing folder full of context before starting work, target/bullseye icon for focus.",
    "ให้ context ที่ครบก่อน แล้วผลลัพธ์จะแม่นขึ้น"),
 "03-constraints": ("Guardrails and clear boundary markers on a path leading a robot straight to a goal flag, constraints guiding direction.",
    "กำหนดขอบเขตชัด ๆ ช่วยให้ Claude ทำตรงเป้า"),
 "03-think-first": ("A robot with a glowing thought bubble containing a small plan/blueprint before picking up tools, plan-before-act concept.",
    "ให้คิดและวางแผนก่อน แล้วค่อยลงมือเขียนโค้ด"),
 "03-iterative": ("A spiral loop of refinement: a rough sketch becoming a polished result through repeated improvement arrows.",
    "ค่อย ๆ ปรับทีละรอบ จนได้ผลลัพธ์ที่ดี"),
 "03-mistakes": ("A friendly warning scene: crossed-out vague prompt bubbles versus a clear green-check prompt, do-and-dont contrast.",
    "เลี่ยงข้อผิดพลาดที่พบบ่อยเวลาสั่งงาน Claude"),
 "04-error-debug": ("A magnifying glass tracing a red error bug down through layers of code to its root cause at the bottom, detective theme.",
    "ไล่หาต้นตอที่แท้จริงของ error ไม่ใช่แค่ปลายเหตุ"),
 "04-code-review": ("A robot reviewing code on a screen with approve and comment annotations, friendly senior-reviewer concept.",
    "ใช้ Claude เป็นผู้ช่วยรีวิวโค้ดเหมือน senior dev"),
 "04-security": ("A shield scanning code for vulnerabilities with a radar sweep highlighting a locked padlock, security audit theme.",
    "สแกนหาช่องโหว่ด้านความปลอดภัยในโค้ด"),
 "04-performance": ("A speedometer and a rocket next to optimized code, with a slow snail transforming into fast lightning, performance boost theme.",
    "หาและแก้จุดที่ทำให้แอปช้า ให้เร็วขึ้น"),
 "05-unit-tests": ("A robot generating small green test tubes with checkmarks next to functions, unit testing concept, tidy lab style.",
    "ให้ Claude สร้าง unit test ครอบคลุมฟังก์ชัน"),
 "05-e2e": ("A browser window being automatically clicked through a user flow by a robot hand, end-to-end browser testing theme.",
    "ทดสอบ E2E จำลองการใช้งานจริงผ่านเบราว์เซอร์"),
 "05-api-docs": ("Code transforming into a clean documentation page with API endpoints listed, auto-generated docs concept.",
    "สร้างเอกสาร API อัตโนมัติจากโค้ด"),
 "05-tdd": ("A red failing test turning green after code is written, red-green-refactor cycle shown as a loop.",
    "TDD: เขียนเทสก่อน (แดง) → เขียนโค้ดให้ผ่าน (เขียว) → ปรับปรุง"),
 "06-system-design": ("A blueprint map of connected services, databases and APIs as glowing nodes, an architect robot planning a system.",
    "ปรึกษา Claude เรื่องการออกแบบสถาปัตยกรรมระบบ"),
 "06-refactor": ("Tangled messy code threads being neatly reorganized into clean parallel lines by a robot, recycling/refactor arrows.",
    "รีแฟคเตอร์โค้ดก้อนใหญ่ให้สะอาดและเข้าใจง่าย"),
 "06-migration": ("A bridge carrying code from a JavaScript island to a TypeScript island, migration/upgrade rocket theme.",
    "ย้ายโค้ด เช่น JS→TS หรือ Class→Hooks อย่างเป็นระบบ"),
 "06-db-design": ("Database cylinders connected by relationship lines forming a clean schema diagram, table icons, data design theme.",
    "ออกแบบโครงสร้างฐานข้อมูล (schema) ที่ดี"),
 "07-mcp-intro": ("A central robot with universal plug-in ports connecting to external tools and data sources, MCP connector hub concept.",
    "MCP = ปลั๊กมาตรฐานให้ Claude ต่อกับเครื่องมือภายนอก"),
 "07-mcp-db": ("A robot plugging directly into a glowing database cylinder through an MCP connector cable, live data access theme.",
    "เชื่อมฐานข้อมูลเข้ากับ Claude ผ่าน MCP"),
 "07-slash-commands": ("A command palette with a slash prompt triggering custom shortcut actions as glowing buttons, automation shortcuts theme.",
    "สร้าง slash command ของตัวเองเพื่อสั่งงานซ้ำ ๆ"),
 "07-hooks": ("Gears and a fishing-hook icon automatically triggering scripts at events in a pipeline, automation hooks concept.",
    "Hooks สั่งให้ทำงานอัตโนมัติเมื่อเกิดเหตุการณ์"),
 "07-multi-agent": ("Several specialized robots working together in parallel on different parts of a project, coordinated team theme.",
    "ใช้หลาย agent ทำงานพร้อมกันแบบทีม"),
 "07-headless": ("A robot running silently inside a CI/CD pipeline of connected stages with green checkmarks, no GUI, automation server theme.",
    "รัน Claude แบบ headless ในระบบ CI/CD อัตโนมัติ"),
 "08-design": ("A designer robot sketching a website wireframe and color palette on a canvas, planning phase of a portfolio site.",
    "เฟส 1: ออกแบบเว็บ Portfolio ร่วมกับ Claude"),
 "08-build": ("A robot assembling website blocks into a live portfolio page, build-and-iterate construction theme.",
    "เฟส 2: ลงมือสร้างและปรับแต่งเว็บทีละส่วน"),
}

# deploy.html อยู่ที่ root (บท 8.3)
DEPLOY = {
 "deploy": ("A finished website launching online via a rocket to a cloud server with a globe and a live URL link icon, deployment celebration theme.",
    "เฟส 3: นำเว็บขึ้นออนไลน์ให้คนทั้งโลกเข้าได้"),
}

def _api_key():
    """Accept either GEMINI_API_KEY (preferred) or GEMINI_KEY."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY")
    if not key:
        raise SystemExit("Set GEMINI_API_KEY (or GEMINI_KEY) to generate images.")
    return key

def gen(slug, subject, retries=4):
    key = _api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    body = {"contents":[{"parts":[{"text": build_prompt(slug, subject)}]}],
            "generationConfig":{"responseModalities":["IMAGE"]}}
    data = json.dumps(body).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
            resp = urllib.request.urlopen(req, timeout=180)
            payload = json.loads(resp.read())
            for p in payload["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    return base64.b64decode(p["inlineData"]["data"])
            raise RuntimeError("no image in response: " + json.dumps(payload)[:300])
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
            wait = 2 ** (attempt+1)
            msg = e.read().decode()[:300] if isinstance(e, urllib.error.HTTPError) else str(e)
            print(f"  ! attempt {attempt+1} failed: {msg} -> retry in {wait}s")
            time.sleep(wait)
    return None

def save_webp(raw, path):
    from PIL import Image
    im = Image.open(BytesIO(raw)).convert("RGB")
    # crop to square center then resize to 880px (lesson width)
    w,h = im.size; s=min(w,h)
    im = im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((880,880), Image.LANCZOS)
    im.save(path, "WEBP", quality=82, method=6)

def main():
    os.makedirs(OUT, exist_ok=True)
    items = {**LESSONS, **DEPLOY}
    if ONLY:
        items = {k:v for k,v in items.items() if k in ONLY}
    todo = [(k,v) for k,v in items.items()
            if FORCE or not os.path.exists(os.path.join(OUT, k+".webp"))]
    print(f"{len(todo)} image(s) to generate (of {len(items)})")
    for i,(slug,(subject,_)) in enumerate(todo,1):
        print(f"[{i}/{len(todo)}] {slug} ...", flush=True)
        raw = gen(slug, subject)
        if raw is None:
            print(f"  FAILED {slug}"); continue
        path = os.path.join(OUT, slug+".webp")
        save_webp(raw, path)
        print(f"  saved {path} ({os.path.getsize(path)} bytes)")
        time.sleep(1)
    print("done")

if __name__ == "__main__":
    main()
