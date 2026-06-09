#!/usr/bin/env python3
"""ขยายเนื้อหาบทเรียนให้ละเอียด เข้าใจง่ายขึ้น ด้วย Gemini 2.5 Flash
- อ้างอิงจากเนื้อหาเดิม (ไม่แต่งข้อมูลเท็จเกี่ยวกับ Claude Code)
- ผลลัพธ์เป็น JSON ของ "blocks" เก็บที่ data/detail.json
- รันซ้ำได้ (ข้ามที่มีแล้ว), --force สร้างใหม่, ระบุ slug เพื่อทำเฉพาะบท
"""
import os, sys, json, time, urllib.request, urllib.error

ROOT = os.path.join(os.path.dirname(__file__), "..")
KEY = os.environ["GEMINI_KEY"]
MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
FORCE = "--force" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]

INSTR = (
"คุณเป็นครูสอนเขียนโปรแกรมภาษาไทยที่เก่งมากในการอธิบายให้มือใหม่ (ไม่มีพื้นฐาน) เข้าใจง่าย. "
"ภารกิจ: ขยายเนื้อหาบทเรียนเดิมให้ 'ละเอียดขึ้น ชัดขึ้น และทำตามได้จริง' โดยคงใจความเดิมไว้ "
"ห้ามแต่งข้อมูลที่ไม่จริงเกี่ยวกับ Claude Code (เช่น คำสั่ง/ฟีเจอร์ที่ไม่มีจริง) ถ้าไม่แน่ใจให้พูดกว้าง ๆ. "
"เขียนเป็นภาษาไทยที่อ่านง่าย เป็นกันเอง มีตัวอย่างรูปธรรม และเปรียบเทียบกับชีวิตประจำวันเมื่อช่วยให้เข้าใจ.\n"
"ส่งออกเป็น JSON ตามรูปแบบนี้เป๊ะ ๆ:\n"
'{\n'
'  "blocks": [\n'
'    {\n'
'      "h": "หัวข้อย่อย (สั้น ชัด)",\n'
'      "p": ["ย่อหน้าอธิบาย 1", "ย่อหน้า 2 (ถ้ามี)"],\n'
'      "steps": ["ขั้นที่ 1 ...", "ขั้นที่ 2 ..."],   // ใส่เฉพาะหัวข้อที่เป็นวิธีทำทีละขั้น มิฉะนั้นให้เป็น []\n'
'      "note": "เคล็ดลับ/ข้อควรระวังสั้น ๆ"            // ใส่เมื่อมีประโยชน์ ไม่งั้นเว้นว่าง ""\n'
'    }\n'
'  ]\n'
'}\n'
"กฎ: สร้าง 4-6 blocks, แต่ละ block มี 1-3 ย่อหน้าใน p, ใช้คำง่าย ๆ, "
"เน้นว่า 'ทำไม' และ 'ทำยังไง'. ใช้ <code>...</code> ครอบคำสั่ง/ชื่อไฟล์ได้ในข้อความ. "
"ตอบเป็น JSON ล้วนเท่านั้น."
)

def gen(ctx, retries=4):
    prompt = INSTR + "\n\n=== เนื้อหาบทเรียนเดิม ===\n" + ctx
    body = {"contents":[{"parts":[{"text":prompt}]}],
            "generationConfig":{"temperature":0.6,"responseMimeType":"application/json","maxOutputTokens":4096}}
    data = json.dumps(body).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL, data=data, headers={"Content-Type":"application/json"})
            resp = urllib.request.urlopen(req, timeout=180)
            payload = json.loads(resp.read())
            txt = payload["candidates"][0]["content"]["parts"][0]["text"]
            obj = json.loads(txt)
            if "blocks" in obj and obj["blocks"]:
                return obj
            raise ValueError("no blocks")
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, KeyError, ValueError) as e:
            msg = e.read().decode()[:200] if isinstance(e, urllib.error.HTTPError) else str(e)
            wait = 2**(attempt+1)
            print(f"  ! attempt {attempt+1}: {msg} retry {wait}s")
            time.sleep(wait)
    return None

def main():
    course = json.load(open(os.path.join(ROOT,"data","course.json"),encoding="utf-8"))
    path = os.path.join(ROOT,"data","detail.json")
    detail = json.load(open(path,encoding="utf-8")) if os.path.exists(path) else {}
    todo = []
    for mod in course["modules"]:
        for les in mod["lessons"]:
            if les["slug"]=="deploy": continue
            if ONLY and les["slug"] not in ONLY: continue
            if FORCE or les["slug"] not in detail:
                todo.append(les)
    print(f"{len(todo)} lesson(s) to expand")
    for i,les in enumerate(todo,1):
        c = les.get("content",{})
        ctx = (f"ชื่อบท: {c.get('h1','')}\nเกริ่นนำ: {c.get('intro','')}\n"
               f"หัวข้อย่อยเดิม: {', '.join(c.get('headings',[]))}\n"
               f"เนื้อหาเดิม: {c.get('body_text','')}\nสรุปเดิม: {c.get('takeaways_text','')}")
        print(f"[{i}/{len(todo)}] {les['slug']} ...", flush=True)
        res = gen(ctx)
        if res is None:
            print("  FAILED", les['slug']); continue
        detail[les["slug"]] = res
        json.dump(detail, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  ok ({len(res['blocks'])} blocks)")
        time.sleep(0.4)
    print("done ->", path)

if __name__ == "__main__":
    main()
