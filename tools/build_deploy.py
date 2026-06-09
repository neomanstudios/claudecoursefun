#!/usr/bin/env python3
"""แปลง deploy.html (บท 8.3) ให้เข้าธีม e-learning ใหม่ (light + sidebar)
โดยคงเนื้อหาเดิมไว้ แล้วใส่ override CSS ให้คอมโพเนนต์เฉพาะของหน้านี้เป็นโทนสว่าง
"""
import os, re, html
from build_site import sidebar, FONTS, course

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
/* ---- deploy page specific (light theme overrides) ---- */
.container{max-width:none;margin:0;padding:0}
.hl{background:linear-gradient(135deg,var(--p),var(--teal));-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text}
.hl2{color:var(--teal)}
.sec-head{margin:2.2rem 0 1rem}
.sec-tag{display:inline-block;font-family:var(--mono);font-size:.74rem;font-weight:700;color:var(--p);
  background:var(--p-soft);padding:.2rem .7rem;border-radius:20px;margin-bottom:.5rem}
.sec-head h2{font-size:1.5rem;font-weight:800;margin-bottom:.3rem}
.sec-head p{color:var(--muted);font-size:.95rem}
.intro-box{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.3rem;margin-bottom:1.4rem;box-shadow:var(--shadow)}
.intro-box h3{font-size:1.15rem;font-weight:800;margin-bottom:.6rem}
.intro-box p{color:var(--ink-2);margin-bottom:.6rem}
.quick-nav{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.4rem}
.qn-link{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.5rem .9rem;
  font-size:.85rem;font-weight:600;color:var(--ink-2)}
.qn-link:hover{border-color:var(--p);color:var(--p)}
.compare{overflow-x:auto;margin-bottom:1.4rem}
.compare table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
  border-radius:var(--radius);overflow:hidden;font-size:.9rem}
.compare th{background:var(--bg);text-align:left;padding:.7rem .9rem;font-weight:800;color:var(--ink);
  border-bottom:1px solid var(--line)}
.compare td{padding:.7rem .9rem;border-bottom:1px solid var(--line-2);color:var(--ink-2)}
.compare tr:last-child td{border-bottom:none}
.badge-best{display:inline-block;background:var(--green-soft);color:var(--green);font-size:.7rem;
  font-weight:700;padding:.1rem .5rem;border-radius:20px;margin-left:.3rem}
.platform{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.4rem;margin-bottom:1.4rem;box-shadow:var(--shadow)}
.plat-head{display:flex;gap:.9rem;align-items:flex-start;margin-bottom:.9rem}
.plat-logo{width:46px;height:46px;border-radius:12px;background:var(--p-soft);display:flex;
  align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0}
.plat-name{font-size:1.15rem;font-weight:800}
.plat-tagline{color:var(--muted);font-size:.86rem;margin:.15rem 0 .4rem}
.plat-tags{display:flex;flex-wrap:wrap;gap:.4rem}
.ptag{font-size:.72rem;font-weight:700;padding:.18rem .55rem;border-radius:20px}
.ptag-free{background:var(--green-soft);color:var(--green)}
.ptag-fast{background:var(--p-soft);color:var(--p)}
.ptag-easy{background:var(--teal-soft);color:var(--teal)}
.plat-best{background:var(--bg);border-left:3px solid var(--teal);border-radius:8px;padding:.7rem .9rem;
  font-size:.88rem;color:var(--ink-2);margin-bottom:1rem}
.plat-best strong{color:var(--ink)}
.way{border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;margin-bottom:1rem}
.way-easy{background:var(--teal-soft);border-color:#BFEBE4}
.way-manual{background:var(--bg)}
.way-title{font-weight:800;font-size:.98rem;margin-bottom:.6rem}
.action-list{list-style:none;margin:.3rem 0}
.action-list li{display:flex;gap:.7rem;align-items:flex-start;margin-bottom:.6rem}
.action-num{width:24px;height:24px;border-radius:50%;background:var(--p);color:#fff;font-weight:800;
  font-size:.78rem;font-family:var(--mono);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.action-text{color:var(--ink-2);font-size:.92rem;line-height:1.65}
.action-text strong{color:var(--ink)}
.action-text small{display:block;color:var(--muted);font-size:.8rem;margin-top:.2rem}
.result-url{display:flex;gap:.6rem;align-items:center;background:var(--green-soft);border:1px solid #BFE8CE;
  border-radius:10px;padding:.7rem .9rem;margin-top:.8rem;color:#0d6b3a;font-size:.9rem}
.result-url .ri{font-size:1.2rem}
.terminal{background:#1B1F2E;border-radius:10px;overflow:hidden;margin:.6rem 0}
.term-bar{display:flex;align-items:center;gap:.4rem;padding:.5rem .8rem;background:#262B3D}
.tdot{width:11px;height:11px;border-radius:50%}
.term-title{color:#cfd3e6;font-size:.78rem;margin-left:.4rem;font-family:var(--mono)}
.term-body{padding:.8rem 1rem;font-family:var(--mono);font-size:.84rem;color:#E7E9F3;white-space:pre-wrap;line-height:1.7}
.prompt{color:#7CFFB2}.cmd{color:#E7E9F3}.cmt{color:#8b93a7}.ok{color:#7CFFB2}
.copy-cmd{background:var(--p);color:#fff;border:none;border-radius:8px;padding:.35rem .8rem;
  font-size:.78rem;font-weight:700;font-family:var(--font);cursor:pointer;margin-top:-.2rem}
.domain-box{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:1.4rem;margin-bottom:1.4rem;box-shadow:var(--shadow)}
.note-warn{background:#FDECEC;border:1px solid #F3C2C2;border-left:4px solid var(--coral)}
.note-tip{background:var(--teal-soft);border:1px solid #BFEBE4;border-left:4px solid var(--teal)}
.next-section{margin-top:2rem}
.next-box{background:linear-gradient(135deg,var(--p-soft),var(--teal-soft));border:1px solid var(--line);
  border-radius:18px;padding:2rem;text-align:center}
.next-box .mt,.next-box p{color:var(--ink-2)}
.go-btn{display:inline-flex;align-items:center;gap:.4rem;background:var(--p);color:#fff;font-weight:700;
  padding:.65rem 1.3rem;border-radius:11px}
.go-link{display:inline-flex;align-items:center;gap:.4rem;background:var(--card);border:1px solid var(--line);
  color:var(--ink);font-weight:700;padding:.65rem 1.3rem;border-radius:11px}
.fade-up{opacity:1}
code{color:#5B3BC4}
"""

# prev = บทสุดท้ายก่อน deploy (08-build)
flat = [l for m in course["modules"] for l in m["lessons"]]
di = next(i for i,l in enumerate(flat) if l["slug"]=="deploy")
prev = flat[di-1] if di>0 else None
prev_btn = (f'<a href="{prev["href"][len("lessons/"):] if prev["href"].startswith("lessons/") else prev["href"]}" '
            f'class="pn-btn"><span class="pn-dir">← ก่อนหน้า</span>'
            f'<span class="pn-title">{html.escape(prev["title"])}</span></a>') if prev else \
           '<span class="pn-btn disabled"><span class="pn-dir">← ก่อนหน้า</span><span class="pn-title">—</span></span>'
# deploy ลิงก์ใน sidebar เป็น "deploy.html" (root) อยู่แล้ว
prev_href = prev["href"]  # lessons/08-build.html — but deploy is at root
prev_btn = (f'<a href="{prev_href}" class="pn-btn"><span class="pn-dir">← ก่อนหน้า</span>'
            f'<span class="pn-title">{html.escape(prev["title"])}</span></a>')

page = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phase 3: Deploy เว็บขึ้นออนไลน์ | Claude Code Hub</title>
<meta name="description" content="เอาเว็บขึ้นออนไลน์ฟรี ด้วย Cloudflare Pages, Vercel, GitHub Pages หรือ Netlify ทำตามทีละขั้น">
{FONTS}
<link rel="stylesheet" href="assets/app.css">
<style>{OVERRIDE}</style>
</head>
<body data-slug="deploy">
<div class="reading-bar" id="bar"></div>
<div class="sb-overlay"></div>
{sidebar("deploy", False)}
<div class="main">
  <div class="topbar"><button class="hamb" id="hamb" aria-label="เมนู">☰</button>
    <span class="tb-title">8. Workshop: Deploy</span></div>
  <div class="docs">
    <article class="reading">
      <div class="crumb"><a href="index.html">หน้าหลัก</a> › โมดูล 8: Workshop สร้าง Portfolio Website</div>
      <span class="les-no">บทเรียน 8.3</span>
      <h1>เอาเว็บขึ้นออนไลน์ ให้คนทั้งโลกเห็น</h1>
      <p class="lead">เว็บที่รันบนเครื่องคุณ พร้อมแชร์แล้ว! เลือกแพลตฟอร์มที่ชอบแล้วทำตามทีละขั้น —
         หรือให้ Claude ช่วย deploy ให้ก็ได้ ทุกแพลตฟอร์มในบทนี้มีแพลนฟรี</p>
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
