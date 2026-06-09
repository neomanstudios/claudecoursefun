#!/usr/bin/env python3
"""ดึงโครงสร้างคอร์ส (จาก index.html) + เนื้อหาบทเรียนแต่ละบท → data/course.json
ใช้เป็น single source of truth สำหรับ build_site.py
"""
import os, re, json, html

ROOT = os.path.join(os.path.dirname(__file__), "..")
INDEX = os.path.join(ROOT, "index.html")
LESSONS = os.path.join(ROOT, "lessons")

def parse_modules():
    src = open(INDEX, encoding="utf-8").read()
    mods = []
    # each module = <details ...><summary>...</summary> ... </details>
    for mblock in re.finditer(r'<details class="module[^"]*"[^>]*>(.*?)</details>', src, re.S):
        body = mblock.group(1)
        mnum = re.search(r'<span class="mnum">(.*?)</span>', body, re.S)
        mtitle = re.search(r'<span class="mtitle">(.*?)</span>', body, re.S)
        msub = re.search(r'<span class="msub">(.*?)</span>', body, re.S)
        lessons = []
        for a in re.finditer(r'<a href="([^"]+)" class="ll">\s*<span class="i">(.*?)</span>\s*<span class="n">(.*?)</span>(.*?)</a>', body, re.S):
            href, icon, num, title = a.groups()
            lessons.append({
                "href": href.strip(),
                "slug": re.sub(r'(lessons/|\.html$)', '', href.strip()),
                "icon": icon.strip(),
                "num": num.strip(),
                "title": html.unescape(title.strip()),
            })
        mods.append({
            "num": mnum.group(1).strip() if mnum else "",
            "title": html.unescape(mtitle.group(1).strip()) if mtitle else "",
            "sub": html.unescape(msub.group(1).strip()) if msub else "",
            "lessons": lessons,
        })
    return mods

def strip_tags(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def extract_lesson(path):
    src = open(path, encoding="utf-8").read()
    out = {}
    m = re.search(r'<div class="lesson-no">(.*?)</div>', src, re.S)
    out["lesson_no"] = strip_tags(m.group(1)) if m else ""
    m = re.search(r'<h1>(.*?)</h1>', src, re.S)
    out["h1"] = strip_tags(m.group(1)) if m else ""
    m = re.search(r'<div class="intro">(.*?)</div>', src, re.S)
    out["intro"] = strip_tags(m.group(1)) if m else ""
    # body = everything from first .block to before .pagenav
    body = ""
    bm = re.search(r'(<div class="block">.*?)(?=<div class="pagenav">)', src, re.S)
    if bm:
        body = bm.group(1).strip()
    out["body_html"] = body
    out["body_text"] = strip_tags(body)[:2500]
    # takeaways list items
    tk = re.findall(r'<div class="takeaways">.*?</div>', src, re.S)
    out["takeaways_text"] = strip_tags(tk[0]) if tk else ""
    # block headings
    out["headings"] = [strip_tags(h) for h in re.findall(r'<div class="block"><h3>(.*?)</h3>', src, re.S)]
    return out

def main():
    mods = parse_modules()
    flat = []
    for mi, mod in enumerate(mods):
        for li, les in enumerate(mod["lessons"]):
            flat.append((mi, li, les))
    # attach prev/next and content
    for idx,(mi,li,les) in enumerate(flat):
        path = os.path.join(ROOT, les["href"])
        if os.path.exists(path):
            les["content"] = extract_lesson(path)
        else:
            les["content"] = {}
            print("  ! missing", path)
        les["module_title"] = mods[mi]["title"]
        les["module_num"] = mods[mi]["num"]
        les["global_index"] = idx
        les["prev"] = flat[idx-1][2]["href"] if idx>0 else None
        les["prev_title"] = flat[idx-1][2]["title"] if idx>0 else None
        les["next"] = flat[idx+1][2]["href"] if idx<len(flat)-1 else None
        les["next_title"] = flat[idx+1][2]["title"] if idx<len(flat)-1 else None
    course = {"modules": mods, "total": len(flat)}
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    json.dump(course, open(os.path.join(ROOT,"data","course.json"),"w",encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"parsed {len(mods)} modules, {len(flat)} lessons -> data/course.json")

if __name__ == "__main__":
    main()
