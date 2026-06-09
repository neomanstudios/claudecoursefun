#!/usr/bin/env python3
"""แปลง deploy.html (บท 8.3) ให้เข้าธีม e-learning ใหม่ (light + sidebar)
โดยคงเนื้อหาเดิมไว้ แล้วใส่ override CSS ให้คอมโพเนนต์เฉพาะของหน้านี้เป็นโทนสว่าง
"""
import os, re, html
from build_site import sidebar, FONTS, course, HEAD_THEME, theme_toggle

ROOT = os.path.join(os.path.dirname(__file__), "..")
src = open(os.path.join(ROOT,"deploy.html"),encoding="utf-8").read()

# ดึงเนื้อหาตั้งแต่ <div class="container"> แรก ถึงก่อน <footer>
start = src.index('<div class="container">')
end = src.index('<footer>')
body = src[start:end].strip()
# ลบ figure เดิม (inline dark) — จะใส่ figure สะอาดใหม่
body = re.sub(r'<figure class="lesson-hero".*?</figure>', '', body, flags=re.S)

clean_fig = ('<figure class="lesson-hero"><img src="images/deploy.webp" '
  'alt="เฟส 3: นำเว็บขึ้นออนไลน์ให้คนทั้งโลกเข้าได้" loading="lazy" decoding="async">'
  '<figcaption>🖼️ เฟส 3: นำเว็บขึ้นออนไลน์ ให้คนทั้งโลกเข้าถึงเว็บของคุณได้</figcaption></figure>')

OVERRIDE = """
/* ---- deploy page specific (themed via design tokens, dark-aware) ----
   page accent = --mc (module 8 = teal); primary buttons = --accent */
.container{max-width:none;margin:0;padding:0}
.hl{background:linear-gradient(135deg,var(--mc),var(--accent-2));-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text}
.hl2{color:var(--mc)}
.sec-head{margin:2.2rem 0 1rem}
.sec-tag{display:inline-block;font-family:var(--mono);font-size:.74rem;font-weight:700;color:var(--mc);
  background:color-mix(in srgb,var(--mc) 14%,transparent);padding:.2rem .7rem;border-radius:20px;margin-bottom:.5rem}
.sec-head h2{font-family:var(--font-display);font-size:1.5rem;font-weight:700;margin-bottom:.3rem;color:var(--ink)}
.sec-head p{color:var(--muted);font-size:.95rem}
.intro-box{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.3rem;margin-bottom:1.4rem;box-shadow:var(--shadow-sm)}
.intro-box h3{font-family:var(--font-display);font-size:1.15rem;font-weight:600;margin-bottom:.6rem;color:var(--ink)}
.intro-box p{color:var(--ink-2);margin-bottom:.6rem}
.quick-nav{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.4rem}
.qn-link{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.5rem .9rem;
  font-size:.85rem;font-weight:600;color:var(--ink-2);transition:.15s}
.qn-link:hover{border-color:var(--mc);color:var(--mc)}
.compare{overflow-x:auto;margin-bottom:1.4rem}
.compare table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
  border-radius:var(--radius);overflow:hidden;font-size:.9rem}
.compare th{background:var(--bg-2);text-align:left;padding:.7rem .9rem;font-weight:700;color:var(--ink);
  border-bottom:1px solid var(--line)}
.compare td{padding:.7rem .9rem;border-bottom:1px solid var(--line-2);color:var(--ink-2)}
.compare tr:last-child td{border-bottom:none}
.badge-best{display:inline-block;background:var(--ok-soft);color:var(--ok-ink);font-size:.7rem;
  font-weight:700;padding:.1rem .5rem;border-radius:20px;margin-left:.3rem}
.platform{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.4rem;margin-bottom:1.4rem;box-shadow:var(--shadow-sm)}
.plat-head{display:flex;gap:.9rem;align-items:flex-start;margin-bottom:.9rem}
.plat-logo{width:46px;height:46px;border-radius:13px;background:color-mix(in srgb,var(--mc) 15%,transparent);
  display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0}
.plat-name{font-family:var(--font-display);font-size:1.15rem;font-weight:600;color:var(--ink)}
.plat-tagline{color:var(--muted);font-size:.86rem;margin:.15rem 0 .4rem}
.plat-tags{display:flex;flex-wrap:wrap;gap:.4rem}
.ptag{font-size:.72rem;font-weight:700;padding:.18rem .55rem;border-radius:20px}
.ptag-free{background:var(--ok-soft);color:var(--ok-ink)}
.ptag-fast{background:var(--accent-soft);color:var(--accent)}
.ptag-easy{background:color-mix(in srgb,var(--accent-2) 16%,transparent);color:var(--accent-2)}
.plat-best{background:var(--bg-2);border-left:3px solid var(--mc);border-radius:8px;padding:.7rem .9rem;
  font-size:.88rem;color:var(--ink-2);margin-bottom:1rem}
.plat-best strong{color:var(--ink)}
.way{border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;margin-bottom:1rem}
.way-easy{background:color-mix(in srgb,var(--mc) 9%,var(--card));border-color:color-mix(in srgb,var(--mc) 26%,var(--line))}
.way-manual{background:var(--bg-2)}
.way-title{font-family:var(--font-display);font-weight:600;font-size:.98rem;margin-bottom:.6rem;color:var(--ink)}
.action-list{list-style:none;margin:.3rem 0}
.action-list li{display:flex;gap:.7rem;align-items:flex-start;margin-bottom:.6rem}
.action-num{width:24px;height:24px;border-radius:50%;background:var(--mc);color:#fff;font-weight:800;
  font-size:.78rem;font-family:var(--mono);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.action-text{color:var(--ink-2);font-size:.92rem;line-height:1.65}
.action-text strong{color:var(--ink)}
.action-text small{display:block;color:var(--muted);font-size:.8rem;margin-top:.2rem}
.result-url{display:flex;gap:.6rem;align-items:center;background:var(--ok-soft);
  border:1px solid color-mix(in srgb,var(--ok) 40%,transparent);
  border-radius:10px;padding:.7rem .9rem;margin-top:.8rem;color:var(--ok-ink);font-size:.9rem}
.result-url .ri{font-size:1.2rem}
.terminal{background:#101320;border:1px solid #232838;border-radius:12px;overflow:hidden;margin:.6rem 0}
.term-bar{display:flex;align-items:center;gap:.4rem;padding:.5rem .8rem;background:#1a1f30}
.tdot{width:11px;height:11px;border-radius:50%}
.term-title{color:#cfd3e6;font-size:.78rem;margin-left:.4rem;font-family:var(--mono)}
.term-body{padding:.8rem 1rem;font-family:var(--mono);font-size:.84rem;color:#E7E9F3;white-space:pre-wrap;line-height:1.7}
.prompt{color:#7CFFB2}.cmd{color:#E7E9F3}.cmt{color:#8b93a7}.ok{color:#7CFFB2}
.copy-cmd{background:var(--accent);color:var(--accent-ink);border:none;border-radius:8px;padding:.35rem .8rem;
  font-size:.78rem;font-weight:700;font-family:var(--font-display);cursor:pointer;margin-top:-.2rem}
.domain-box{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.4rem;margin-bottom:1.4rem;box-shadow:var(--shadow-sm)}
.note-warn{background:var(--bad-soft);border:1px solid color-mix(in srgb,var(--bad) 35%,transparent);border-left:4px solid var(--bad)}
.note-tip{background:color-mix(in srgb,var(--accent-2) 12%,var(--card));border:1px solid color-mix(in srgb,var(--accent-2) 30%,var(--line));border-left:4px solid var(--accent-2)}
.next-section{margin-top:2rem}
.next-box{background:linear-gradient(135deg,color-mix(in srgb,var(--mc) 14%,var(--card)),color-mix(in srgb,var(--accent-2) 12%,var(--card)));
  border:1px solid color-mix(in srgb,var(--mc) 26%,var(--line));border-radius:18px;padding:2rem;text-align:center}
.next-box .mt{font-family:var(--font-display);font-weight:700;font-size:1.2rem;color:var(--ink);margin-bottom:.4rem;display:block}
.next-box p{color:var(--ink-2)}
.go-btn{display:inline-flex;align-items:center;gap:.4rem;background:var(--accent);color:var(--accent-ink);
  font-family:var(--font-display);font-weight:700;padding:.7rem 1.4rem;border-radius:12px}
.go-link{display:inline-flex;align-items:center;gap:.4rem;background:var(--card);border:1px solid var(--line);
  color:var(--ink);font-weight:700;padding:.7rem 1.4rem;border-radius:12px}
.fade-up{opacity:1}
"""

# prev = บทสุดท้ายก่อน deploy (08-build); deploy อยู่ root, ใช้ href "lessons/..." ได้เลย
flat = [l for m in course["modules"] for l in m["lessons"]]
di = next(i for i,l in enumerate(flat) if l["slug"]=="deploy")
prev = flat[di-1] if di>0 else None
prev_btn = (f'<a href="{prev["href"]}" class="pn-btn"><span class="pn-dir">← ก่อนหน้า</span>'
            f'<span class="pn-title">{html.escape(prev["title"])}</span></a>') if prev else \
           '<span class="pn-btn disabled"><span class="pn-dir">← ก่อนหน้า</span><span class="pn-title">นี่คือบทแรก</span></span>'

page = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phase 3: Deploy เว็บขึ้นออนไลน์ | Claude Code Hub</title>
<meta name="description" content="เอาเว็บขึ้นออนไลน์ฟรี ด้วย Cloudflare Pages, Vercel, GitHub Pages หรือ Netlify ทำตามทีละขั้น">
{HEAD_THEME}
{FONTS}
<link rel="stylesheet" href="assets/app.css">
<style>{OVERRIDE}</style>
</head>
<body data-slug="deploy" data-mod="8">
<div class="reading-bar" id="bar"></div>
<div class="sb-overlay"></div>
{sidebar("deploy", False)}
<div class="main">
  <div class="topbar"><button class="hamb" id="hamb" aria-label="เมนู">☰</button>
    <span class="tb-title">8. Workshop: Deploy</span>
    {theme_toggle()}</div>
  <div class="docs">
    <article class="reading">
      <div class="crumb"><a href="index.html">หน้าหลัก</a> › โมดูล 8: Workshop สร้าง Portfolio Website</div>
      <span class="les-no">บทเรียน 8.3</span>
      <h1>เอาเว็บขึ้นออนไลน์ ให้คนทั้งโลกเห็น</h1>
      <p class="lead">เว็บที่รันบนเครื่องคุณ พร้อมแชร์แล้ว! เลือกแพลตฟอร์มที่ชอบแล้วทำตามทีละขั้น
         หรือจะให้ Claude ช่วย deploy ให้ก็ได้ ทุกแพลตฟอร์มในบทนี้มีแพลนฟรี</p>
      {clean_fig}
      {body}
      <div class="complete-row"><button class="btn-complete" id="btnComplete">✓ ทำเครื่องหมายว่าเรียนจบ</button></div>
      <div class="pagenav">{prev_btn}<span class="pn-btn pn-next disabled"><span class="pn-dir">จบคอร์ส 🎉</span><span class="pn-title">คุณเรียนครบแล้ว!</span></span></div>
    </article>
    <aside class="toc"><div class="toc-t">ในบทนี้</div>
      <a href="#cloudflare">☁️ Cloudflare Pages</a>
      <a href="#vercel">▲ Vercel</a>
      <a href="#github">🐙 GitHub Pages</a>
      <a href="#netlify">🔷 Netlify</a>
      <a href="#domain">🌍 โดเมนของตัวเอง</a>
    </aside>
  </div>
  <footer>Claude Code Learning Hub · Curated by <strong>Chetaphong Preecha</strong> &amp; Beyond Team</footer>
</div>
<script>
function copyText(id,btn){{var t=document.getElementById(id).innerText;
  navigator.clipboard.writeText(t).then(function(){{var o=btn.innerHTML;btn.innerHTML='✅ คัดลอกแล้ว!';
  btn.classList.add('done');setTimeout(function(){{btn.innerHTML=o;btn.classList.remove('done')}},1800)}});}}
</script>
<script src="assets/app.js"></script>
</body>
</html>"""
open(os.path.join(ROOT,"deploy.html"),"w",encoding="utf-8").write(page)
print("rebuilt deploy.html (light LMS theme)")
