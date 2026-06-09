/* Claude Code Learning Hub — shared lesson behaviour
   - ความคืบหน้า (เก็บใน localStorage)  - แบบทดสอบโต้ตอบ  - ปุ่มคัดลอก  - เมนูมือถือ */
(function(){
  var KEY='cc_progress_v1';
  function load(){try{return JSON.parse(localStorage.getItem(KEY))||[]}catch(e){return[]}}
  function save(a){localStorage.setItem(KEY,JSON.stringify(a))}
  function done(){return load()}
  function isDone(slug){return done().indexOf(slug)>-1}
  function setDone(slug,v){var a=load();var i=a.indexOf(slug);
    if(v&&i<0)a.push(slug); if(!v&&i>-1)a.splice(i,1); save(a);}

  // ---- sidebar progress + active + checkmarks ----
  function refreshSidebar(){
    // mark done state on every lesson link (sidebar + หน้าหลัก)
    document.querySelectorAll('.sb-les a[data-slug]').forEach(function(a){
      if(isDone(a.getAttribute('data-slug')))a.classList.add('done');else a.classList.remove('done');
    });
    // นับความคืบหน้าจาก sidebar เท่านั้น (กันนับซ้ำกับการ์ดในหน้าหลัก)
    var counted=document.querySelectorAll('.sidebar .sb-les a[data-slug]');
    var total=counted.length, n=0;
    counted.forEach(function(a){if(isDone(a.getAttribute('data-slug')))n++;});
    var bar=document.querySelector('.sb-bar i');
    var pct=total?Math.round(n/total*100):0;
    if(bar)bar.style.width=pct+'%';
    var lbl=document.querySelector('.sb-progress .lbl b');
    if(lbl)lbl.textContent=n+'/'+total+' บท ('+pct+'%)';
  }

  // ---- mark complete ----
  function initComplete(){
    var btn=document.getElementById('btnComplete');
    if(!btn)return;
    var slug=document.body.getAttribute('data-slug');
    function paint(){
      if(isDone(slug)){btn.classList.add('done');btn.innerHTML='✓ เรียนจบบทนี้แล้ว (กดเพื่อยกเลิก)';}
      else{btn.classList.remove('done');btn.innerHTML='✓ ทำเครื่องหมายว่าเรียนจบ';}
    }
    btn.addEventListener('click',function(){setDone(slug,!isDone(slug));paint();refreshSidebar();});
    paint();
  }

  // ---- quiz ----
  function initQuiz(){
    document.querySelectorAll('.q').forEach(function(q){
      var ans=parseInt(q.getAttribute('data-answer'),10);
      var choices=q.querySelectorAll('.choice');
      var ex=q.querySelector('.q-explain');
      choices.forEach(function(c,i){
        c.addEventListener('click',function(){
          if(q.getAttribute('data-locked'))return;
          q.setAttribute('data-locked','1');
          choices.forEach(function(cc,j){
            cc.disabled=true;
            if(j===ans)cc.classList.add('correct');
          });
          if(i!==ans)c.classList.add('wrong');
          if(ex)ex.classList.add('show');
        });
      });
    });
  }

  // ---- copy buttons ----
  window.cp=function(){var el=document.getElementById('pt');if(!el)return;
    navigator.clipboard.writeText(el.innerText);
    var b=document.querySelector('.copy-btn');if(!b)return;var o=b.innerHTML;
    b.innerHTML='✅ คัดลอกแล้ว!';b.classList.add('done');
    setTimeout(function(){b.innerHTML=o;b.classList.remove('done')},1800);};
  window.cc=function(btn){var pre=btn.parentElement.querySelector('pre');
    navigator.clipboard.writeText(pre.innerText);var o=btn.innerHTML;
    btn.innerHTML='✅';setTimeout(function(){btn.innerHTML=o},1500);};

  // ---- reading bar ----
  function initBar(){var bar=document.getElementById('bar');if(!bar)return;
    window.addEventListener('scroll',function(){
      var t=document.documentElement.scrollTop,
          h=document.documentElement.scrollHeight-window.innerHeight;
      bar.style.width=(h>0?t/h*100:0)+'%';});}

  // ---- mobile nav ----
  function initNav(){
    var h=document.getElementById('hamb'),ov=document.querySelector('.sb-overlay');
    function close(){document.body.classList.remove('nav-open');}
    if(h)h.addEventListener('click',function(){document.body.classList.toggle('nav-open');});
    if(ov)ov.addEventListener('click',close);
    document.querySelectorAll('.sb-les a').forEach(function(a){a.addEventListener('click',close);});
  }

  // ---- open module of current lesson ----
  function openActiveModule(){
    var a=document.querySelector('.sb-les a.active');
    if(a){var d=a.closest('details.sb-mod');if(d)d.open=true;
      a.scrollIntoView({block:'center'});}
  }

  // ---- scroll-spy: ไฮไลต์หัวข้อปัจจุบันใน "ในบทนี้" ----
  function initTOC(){
    var links=document.querySelectorAll('.toc a[href^="#"]');
    if(!links.length)return;
    var map={};
    links.forEach(function(a){var t=document.getElementById(a.getAttribute('href').slice(1));
      if(t)map[t.id]=a;});
    var ids=Object.keys(map); if(!ids.length)return;
    function onScroll(){
      var cur=null,top=120;
      ids.forEach(function(id){var el=document.getElementById(id);
        if(el.getBoundingClientRect().top-top<=0)cur=id;});
      if(!cur)cur=ids[0];
      links.forEach(function(a){a.classList.remove('on');});
      map[cur].classList.add('on');
    }
    window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  }

  document.addEventListener('DOMContentLoaded',function(){
    refreshSidebar();initComplete();initQuiz();initBar();initNav();openActiveModule();initTOC();
  });
})();
