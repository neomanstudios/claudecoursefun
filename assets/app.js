/* Claude Code Learning Hub — shared behaviour
   - dark/light theme toggle (persisted)   - scroll reveal
   - progress (localStorage)   - interactive quiz   - copy buttons   - mobile nav */
(function(){
  var KEY='cc_progress_v1', THEME='cc_theme';
  function load(){try{return JSON.parse(localStorage.getItem(KEY))||[]}catch(e){return[]}}
  function save(a){localStorage.setItem(KEY,JSON.stringify(a))}
  function done(){return load()}
  function isDone(slug){return done().indexOf(slug)>-1}
  function setDone(slug,v){var a=load();var i=a.indexOf(slug);
    if(v&&i<0)a.push(slug); if(!v&&i>-1)a.splice(i,1); save(a);}

  // ---- theme toggle ----
  function curTheme(){
    var t=document.documentElement.getAttribute('data-theme');
    if(t)return t;
    return (window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light';
  }
  function paintToggle(){
    var dark=curTheme()==='dark';
    document.querySelectorAll('.theme-toggle').forEach(function(b){
      b.textContent=dark?'☀️':'🌙';
      b.setAttribute('aria-label',dark?'สลับเป็นโหมดสว่าง':'สลับเป็นโหมดมืด');
    });
  }
  function initTheme(){
    paintToggle();
    document.querySelectorAll('.theme-toggle').forEach(function(b){
      b.addEventListener('click',function(){
        var next=curTheme()==='dark'?'light':'dark';
        document.documentElement.setAttribute('data-theme',next);
        try{localStorage.setItem(THEME,next);}catch(e){}
        paintToggle();
      });
    });
  }

  // ---- scroll reveal (skipped under reduced-motion / no IO -> content stays visible) ----
  function initReveal(){
    if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    if(!('IntersectionObserver' in window))return;
    var sel='.block,.objectives,figure.lesson-hero,.prompt-box,.takeaways,.quiz,.pagenav,.complete-row';
    var nodes=[].slice.call(document.querySelectorAll(sel));
    [].slice.call(document.querySelectorAll('.reveal')).forEach(function(n){if(nodes.indexOf(n)<0)nodes.push(n);});
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});
    },{rootMargin:'0px 0px -8% 0px',threshold:.08});
    nodes.forEach(function(n){n.classList.add('reveal');io.observe(n);});
    // safety net: never leave content hidden if the observer misfires.
    // Off-screen nodes are revealed invisibly; on failure this rescues them.
    setTimeout(function(){nodes.forEach(function(n){n.classList.add('in');});},2500);
  }

  // ---- sidebar progress + active + checkmarks ----
  function refreshSidebar(){
    document.querySelectorAll('.sb-les a[data-slug], .mc-list a[data-slug]').forEach(function(a){
      if(isDone(a.getAttribute('data-slug')))a.classList.add('done');else a.classList.remove('done');
    });
    // count progress from the sidebar only (avoid double-counting home cards)
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
  window.cp=function(id){var el=document.getElementById(id||'pt');if(!el)return;
    navigator.clipboard.writeText(el.innerText);
    var box=el.closest('.prompt-box');
    var b=box?box.querySelector('.copy-btn'):document.querySelector('.copy-btn');if(!b)return;var o=b.innerHTML;
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
      bar.style.width=(h>0?t/h*100:0)+'%';},{passive:true});}

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

  // ---- scroll-spy: highlight current heading in "ในบทนี้" ----
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
    initTheme();refreshSidebar();initComplete();initQuiz();initBar();initNav();
    openActiveModule();initTOC();initReveal();
  });
})();
