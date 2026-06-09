#!/usr/bin/env python3
"""Generate app/search-index.json — a flat client-side search index covering
every dark-LMS lesson + every authored workshop. URLs are relative to app/
(the client prefixes '../' when on a /lessons/ or /workshops/ page).
Run after build_app.py + build_app_workshops.py."""
import os, re, json
from build_app import FLAT as LESSONS, strip_emoji

ROOT = os.path.join(os.path.dirname(__file__), "..")
APP = os.path.join(ROOT, "app")
catalog = json.load(open(os.path.join(ROOT, "data", "workshops.json"), encoding="utf-8"))
cpath = os.path.join(ROOT, "data", "workshops_content.json")
wcontent = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}

def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()

def base(href):
    return href[len("lessons/"):] if href.startswith("lessons/") else href

entries = []

# ---- lessons ----
for l in LESSONS:
    c = l.get("content", {})
    if not c.get("body_html"):
        continue
    title = clean(c.get("h1") or l["title"])
    desc = clean(c.get("intro", ""))
    mod = clean(strip_emoji(l.get("module_title", "")))
    group = f'บทเรียน · โมดูล {l.get("module_num","")}'
    entries.append({
        "t": title, "u": "lessons/" + base(l["href"]), "g": group, "tag": "บทเรียน",
        "d": desc[:120], "k": " ".join([title, desc, mod, l["slug"], l.get("num","")]).lower()
    })

# ---- workshops (only authored ones have a real page) ----
for cat in catalog["categories"]:
    for w in cat["workshops"]:
        if w["slug"] not in wcontent:
            continue
        title = clean(w["title"]); desc = clean(w.get("goal", ""))
        ct = clean(cat["title"])
        g = wcontent[w["slug"]].get("glance", {})
        extra = clean(g.get("summary", ""))
        entries.append({
            "t": title, "u": "workshops/" + w["slug"] + ".html", "g": f"เวิร์กช็อป · {ct}", "tag": "เวิร์กช็อป",
            "d": desc[:120], "k": " ".join([title, desc, ct, extra, w["slug"]]).lower()
        })

out = os.path.join(APP, "search-index.json")
json.dump(entries, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"built app/search-index.json — {len(entries)} entries "
      f"({sum(1 for e in entries if e['tag']=='บทเรียน')} lessons, "
      f"{sum(1 for e in entries if e['tag']=='เวิร์กช็อป')} workshops)")
