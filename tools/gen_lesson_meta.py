#!/usr/bin/env python3
"""สร้าง 'จุดประสงค์การเรียนรู้' + 'แบบทดสอบท้ายบท' (quiz) ของแต่ละบท
ด้วย Gemini 2.5 Flash (ภาษาไทย) อ้างอิงจากเนื้อหาจริงของบทนั้น
ผลลัพธ์เก็บที่ data/meta.json (รันซ้ำได้ ข้ามบทที่มีแล้ว, --force เพื่อสร้างใหม่)
"""
import os, sys, json, time, urllib.request, urllib.error

ROOT = os.path.join(os.path.dirname(__file__), "..")
KEY = os.environ["GEMINI_KEY"]
MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
FORCE = "--force" in sys.argv

SCHEMA_INSTR = (
"คุณเป็นผู้ออกแบบสื่อการสอนภาษาไทยสำหรับผู้เริ่มต้น (ไม่มีพื้นฐานเขียนโค้ด). "
"จากเนื้อหาบทเรียนด้านล่าง ให้สร้าง JSON ภาษาไทยที่อ่านง่ายมาก ตามรูปแบบนี้เป๊ะ ๆ:\n"
'{\n'
'  "objectives": ["...", "...", "..."],   // 3 ข้อ สิ่งที่ผู้เรียนจะทำได้หลังเรียนจบ ขึ้นต้นด้วยคำกริยา สั้น กระชับ\n'
'  "summary": "...",                         // สรุปบทใน 1-2 ประโยค ภาษาง่ายมาก\n'
'  "quiz": [\n'
'    {"q":"คำถาม", "choices":["ก","ข","ค","ง"], "answer":0, "explain":"เฉลยสั้น ๆ ว่าทำไม"},\n'
'    {"q":"คำถาม", "choices":["ก","ข","ค","ง"], "answer":2, "explain":"..."}\n'
'  ]\n'
'}\n'
"กฎ: 2 คำถาม, แต่ละข้อมี 4 ตัวเลือก, answer คือ index (0-3) ของคำตอบถูก. "
"ใช้ภาษาพูดง่าย ๆ เหมาะมือใหม่. ตอบเป็น JSON ล้วน ห้ามมีข้อความอื่น."
)

def gen(ctx, retries=4):
    prompt = SCHEMA_INSTR + "\n\n=== เนื้อหาบทเรียน ===\n" + ctx
    body = {"contents":[{"parts":[{"text":prompt}]}],
            "generationConfig":{"temperature":0.4,"responseMimeType":"application/json"}}
    data = json.dumps(body).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL, data=data, headers={"Content-Type":"application/json"})
            resp = urllib.request.urlopen(req, timeout=120)
            payload = json.loads(resp.read())
            txt = payload["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(txt)
        except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            msg = e.read().decode()[:200] if isinstance(e, urllib.error.HTTPError) else str(e)
            wait = 2**(attempt+1)
            print(f"  ! attempt {attempt+1}: {msg} retry {wait}s")
            time.sleep(wait)
    return None

def main():
    course = json.load(open(os.path.join(ROOT,"data","course.json"),encoding="utf-8"))
    meta_path = os.path.join(ROOT,"data","meta.json")
    meta = json.load(open(meta_path,encoding="utf-8")) if os.path.exists(meta_path) else {}
    todo = []
    for mod in course["modules"]:
        for les in mod["lessons"]:
            if FORCE or les["slug"] not in meta:
                todo.append(les)
    print(f"{len(todo)} lesson meta to generate")
    for i,les in enumerate(todo,1):
        c = les.get("content",{})
        ctx = (f"ชื่อบท: {c.get('h1','')}\nเกริ่นนำ: {c.get('intro','')}\n"
               f"หัวข้อย่อย: {', '.join(c.get('headings',[]))}\n"
               f"เนื้อหา: {c.get('body_text','')}\nสรุปเดิม: {c.get('takeaways_text','')}")
        print(f"[{i}/{len(todo)}] {les['slug']} ...", flush=True)
        res = gen(ctx)
        if res is None:
            print("  FAILED", les['slug']); continue
        meta[les["slug"]] = res
        json.dump(meta, open(meta_path,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(0.5)
    print("done ->", meta_path)

if __name__ == "__main__":
    main()
