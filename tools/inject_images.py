#!/usr/bin/env python3
"""ฝัง <figure> ภาพประกอบเข้าไปในแต่ละบทเรียน หลังย่อหน้า intro
- รันซ้ำได้: ถ้ามี figure อยู่แล้วจะอัปเดต src/caption ให้ตรง ไม่ซ้อน
"""
import os, re, sys
from gen_images import LESSONS, DEPLOY

ROOT = os.path.join(os.path.dirname(__file__), "..")
LESSONS_DIR = os.path.join(ROOT, "lessons")
IMG_REL_LESSON = "../images/"   # path ใช้ในไฟล์ใต้ lessons/
IMG_REL_ROOT = "images/"        # path ใช้ในไฟล์ที่ root (deploy.html)

MARKER = "lesson-hero"

def figure_html(src, caption, alt):
    return (
f'<figure class="{MARKER}" style="margin:0 0 2rem;border:1px solid rgba(108,99,255,.2);'
f'border-radius:16px;overflow:hidden;background:var(--cd,#12122A);box-shadow:0 8px 30px rgba(0,0,0,.35)">'
f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async" '
f'style="width:100%;display:block;aspect-ratio:16/10;object-fit:cover">'
f'<figcaption style="font-size:.82rem;color:var(--mt,#9999CC);padding:.75rem 1rem;text-align:center;'
f'border-top:1px solid rgba(255,255,255,.06)">🖼️ {caption}</figcaption></figure>'
    )

def inject(path, src, caption, alt, anchor=None):
    html = open(path, encoding="utf-8").read()
    fig = figure_html(src, caption, alt)
    # remove existing hero figure (idempotent)
    html = re.sub(r'<figure class="'+MARKER+r'".*?</figure>', '', html, flags=re.S)
    if anchor:
        # insert right AFTER the matched anchor tag (e.g. opening container div)
        m = re.search(anchor, html, flags=re.S)
        if not m:
            print(f"  ! anchor not found in {path}, skip"); return False
        new = html[:m.end()] + "\n  " + fig + html[m.end():]
        open(path, "w", encoding="utf-8").write(new)
        return True
    # insert right after the intro div's closing tag
    m = re.search(r'(<div class="intro">.*?</div>)', html, flags=re.S)
    if m:
        new = html[:m.end()] + "\n  " + fig + html[m.end():]
    else:
        # fallback: before first .block
        m2 = re.search(r'<div class="block">', html)
        if not m2:
            print(f"  ! no anchor in {path}, skip"); return False
        new = html[:m2.start()] + fig + "\n  " + html[m2.start():]
    open(path, "w", encoding="utf-8").write(new)
    return True

def main():
    n = 0
    for slug,(subject,caption) in LESSONS.items():
        path = os.path.join(LESSONS_DIR, slug+".html")
        webp = os.path.join(ROOT, "images", slug+".webp")
        if not os.path.exists(path):
            print(f"  ! missing lesson {path}"); continue
        if not os.path.exists(webp):
            print(f"  ! missing image for {slug}, skip injection"); continue
        alt = caption
        if inject(path, IMG_REL_LESSON+slug+".webp", caption, alt):
            print(f"  injected {slug}"); n += 1
    # deploy.html at root
    for slug,(subject,caption) in DEPLOY.items():
        path = os.path.join(ROOT, slug+".html")
        webp = os.path.join(ROOT, "images", slug+".webp")
        if os.path.exists(path) and os.path.exists(webp):
            if inject(path, IMG_REL_ROOT+slug+".webp", caption, caption,
                      anchor=r'<div class="container">'):
                print(f"  injected {slug} (root)"); n += 1
    print(f"done: {n} lessons updated")

if __name__ == "__main__":
    main()
