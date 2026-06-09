/* AI Online (dark) — lesson player behaviour: tabs, quiz, copy, progress, nav */
(function(){
  var KEY='cc_progress_v1';
  function load(){try{return JSON.parse(localStorage.getItem(KEY))||[]}catch(e){return[]}}
  function save(a){localStorage.setItem(KEY,JSON.stringify(a))}
  function isDone(s){return load().indexOf(s)>-1}
  function setDone(s,v){var a=load(),i=a.indexOf(s);if(v&&i<0)a.push(s);if(!v&&i>-1)a.splice(i,1);save(a)}

  function refresh(){
    document.querySelectorAll('.lessons a[data-slug],.mc-list a[data-slug]').forEach(function(a){
      a.classList.toggle('done',isDone(a.getAttribute('data-slug')));
    });
    var all=document.querySelectorAll('.sidebar .lessons a[data-slug]');
    var total=all.length,n=0;all.forEach(function(a){if(isDone(a.getAttribute('data-slug')))n++;});
    if(!total){var mc=document.querySelectorAll('.mc-list a[data-slug]');total=mc.length;
      mc.forEach(function(a){if(isDone(a.getAttribute('data-slug')))n++;});}
    var pct=total?Math.round(n/total*100):0;
    var bar=document.querySelector('.pbar i');if(bar)bar.style.width=pct+'%';
    var lbl=document.querySelector('.prog-lbl');if(lbl)lbl.textContent=n+'/'+total+' บท';
    var ri=document.querySelector('.ring-i');if(ri)ri.setAttribute('stroke-dasharray',pct+' 100');
    var rt=document.querySelector('.ring-t');if(rt)rt.textContent=pct+'%';
  }

  function tabs(){
    document.querySelectorAll('.tabs button[data-tab]').forEach(function(b){
      b.addEventListener('click',function(){
        document.querySelectorAll('.tabs button').forEach(function(x){x.classList.remove('on')});
        b.classList.add('on');
        var t=b.getAttribute('data-tab');
        document.querySelectorAll('.tab-panel').forEach(function(p){p.hidden=p.getAttribute('data-panel')!==t;});
      });
    });
    document.querySelectorAll('.toc a.tq').forEach(function(a){a.addEventListener('click',function(e){
      e.preventDefault();var qb=document.querySelector('.tabs button[data-tab="quiz"]');if(qb)qb.click();});});
  }

  function quiz(){
    document.querySelectorAll('.q').forEach(function(q){
      var ans=parseInt(q.getAttribute('data-answer'),10),ch=q.querySelectorAll('.choice'),ex=q.querySelector('.q-explain');
      ch.forEach(function(c,i){c.addEventListener('click',function(){
        if(q.getAttribute('data-locked'))return;q.setAttribute('data-locked','1');
        ch.forEach(function(cc,j){cc.disabled=true;if(j===ans)cc.classList.add('correct');});
        if(i!==ans)c.classList.add('wrong');if(ex)ex.classList.add('show');
      });});
    });
  }

  window.cp=function(id){var el=document.getElementById(id||'pt');if(!el)return;navigator.clipboard.writeText(el.innerText);
    var box=el.closest('.prompt-box, .step-prompt');var b=box?box.querySelector('.copy-btn'):document.querySelector('.copy-btn');if(!b)return;
    var o=b.innerHTML;b.innerHTML='คัดลอกแล้ว';b.classList.add('done');
    setTimeout(function(){b.innerHTML=o;b.classList.remove('done')},1600);};
  window.cc=function(btn){var pre=btn.parentElement.querySelector('pre');if(!pre)return;navigator.clipboard.writeText(pre.innerText);
    var o=btn.innerHTML;btn.innerHTML='✓';setTimeout(function(){btn.innerHTML=o},1400);};

  function complete(){
    var btn=document.getElementById('btnComplete');if(!btn)return;var slug=document.body.getAttribute('data-slug');
    function paint(){if(isDone(slug)){btn.classList.add('done');btn.textContent='เรียนจบบทนี้แล้ว';}
      else{btn.classList.remove('done');btn.textContent='ทำเครื่องหมายว่าเรียนจบ';}}
    btn.addEventListener('click',function(){setDone(slug,!isDone(slug));paint();refresh();});paint();
  }

  function nav(){
    var h=document.querySelector('.hamb'),ov=document.querySelector('.sb-overlay');
    if(h)h.addEventListener('click',function(){document.body.classList.toggle('nav-open')});
    if(ov)ov.addEventListener('click',function(){document.body.classList.remove('nav-open')});
    document.querySelectorAll('.lessons a').forEach(function(a){a.addEventListener('click',function(){document.body.classList.remove('nav-open')})});
    var act=document.querySelector('.sidebar .lessons a.active');if(act)act.scrollIntoView({block:'center'});
  }

  function spy(){
    var links=document.querySelectorAll('.toc a[href^="#"]');if(!links.length)return;
    var map={};links.forEach(function(a){var id=a.getAttribute('href').slice(1),el=document.getElementById(id);if(el)map[id]=a;});
    var ids=Object.keys(map);if(!ids.length)return;
    function on(){var cur=ids[0];ids.forEach(function(id){if(document.getElementById(id).getBoundingClientRect().top-120<=0)cur=id;});
      links.forEach(function(a){a.classList.remove('on')});if(map[cur])map[cur].classList.add('on');}
    window.addEventListener('scroll',on,{passive:true});on();
  }

  // ---- guided stepper: show ONE step at a time with progress + Back/Next ----
  function initSteps(){
    var ARROW='<span class="st-ico"><svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="M5 12h13"/><path d="m12 6 6 6-6 6"/></svg></span>';
    var REDO='<span class="st-ico"><svg class="ic" viewBox="0 0 24 24" style="width:14px"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg></span>';
    var BACK='<svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="m15 18-6-6 6-6"/></svg>';
    var CHECK='<svg class="ic" viewBox="0 0 24 24" style="width:15px"><path d="m5 13 4 4L19 7"/></svg>';
    document.querySelectorAll('ol.steps[data-stepper]').forEach(function(ol){
      var steps=[].slice.call(ol.children).filter(function(n){return n.tagName==='LI';});
      if(steps.length<2)return;
      steps.forEach(function(li,k){li.setAttribute('data-n',k+1);});
      var wrap=document.createElement('div');wrap.className='stepper';
      ol.parentNode.insertBefore(wrap,ol);
      var head=document.createElement('div');head.className='st-head';
      var track=document.createElement('div');track.className='st-track';var segs=[];
      steps.forEach(function(_,k){var s=document.createElement('button');s.type='button';s.className='st-seg';
        s.setAttribute('aria-label','ไปขั้นที่ '+(k+1));s.addEventListener('click',function(){go(k);});track.appendChild(s);segs.push(s);});
      var count=document.createElement('div');count.className='st-count';
      head.appendChild(track);head.appendChild(count);
      var nav=document.createElement('div');nav.className='st-nav';
      var prev=document.createElement('button');prev.type='button';prev.className='st-prev';prev.innerHTML=BACK+'ย้อนกลับ';
      var next=document.createElement('button');next.type='button';next.className='st-next';
      nav.appendChild(prev);nav.appendChild(next);
      wrap.appendChild(head);wrap.appendChild(ol);wrap.appendChild(nav);
      ol.classList.add('is-wired');
      var i=0;
      function render(){
        steps.forEach(function(li,k){li.classList.toggle('active',k===i);});
        segs.forEach(function(s,k){s.classList.toggle('on',k<=i);s.classList.toggle('cur',k===i);});
        count.textContent='ขั้นที่ '+(i+1)+' / '+steps.length;
        prev.disabled=(i===0);
        next.innerHTML=(i===steps.length-1)?('เริ่มทำใหม่'+REDO):('ถัดไป'+ARROW);
      }
      function go(k){i=k<0?0:(k>=steps.length?steps.length-1:k);render();}
      prev.addEventListener('click',function(){if(i>0)go(i-1);});
      next.addEventListener('click',function(){go(i===steps.length-1?0:i+1);});
      wrap.addEventListener('keydown',function(e){
        if(e.key==='ArrowRight'){e.preventDefault();next.click();}
        else if(e.key==='ArrowLeft'){e.preventDefault();if(!prev.disabled)prev.click();}
      });
      render();
    });
    document.querySelectorAll('.step-prompt .sp-copy').forEach(function(btn){
      btn.addEventListener('click',function(){
        var box=btn.closest('.step-prompt'),t=box&&box.querySelector('.sp-text');if(!t)return;
        navigator.clipboard.writeText(t.innerText);
        var o=btn.innerHTML;btn.classList.add('done');btn.innerHTML=CHECK+'คัดลอกแล้ว';
        setTimeout(function(){btn.innerHTML=o;btn.classList.remove('done');},1600);
      });
    });
  }

  // ---- interactive "watch Claude Code work" demo ----
  function initAgentDemo(){
    var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.querySelectorAll('.agentdemo').forEach(function(d){
      var btn=d.querySelector('.ad-run'),items=[].slice.call(d.querySelectorAll('.ad-log li'));
      if(!btn||!items.length)return;var timers=[];
      btn.addEventListener('click',function(){
        timers.forEach(clearTimeout);timers=[];
        items.forEach(function(li){li.classList.remove('show','is-done');});btn.disabled=true;
        items.forEach(function(li,i){timers.push(setTimeout(function(){
          li.classList.add('show');if(i>0)items[i-1].classList.add('is-done');
          if(i===items.length-1){li.classList.add('is-done');btn.disabled=false;btn.textContent='เล่นอีกครั้ง';}
        },reduce?0:i*620));});
      });
    });
  }

  // ---- content search: ⌘K / Ctrl-K command palette over lessons + workshops ----
  function initSearch(){
    var sub=/\/(lessons|workshops)\//.test(location.pathname), pre=sub?'../':'';
    var data=null, loaded=false, active=0, results=[];
    var isMac=/Mac|iPhone|iPad/.test(navigator.platform||'');
    function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
    var ov=document.createElement('div');ov.className='cmdk';ov.hidden=true;
    ov.innerHTML='<div class="cmdk-box" role="dialog" aria-label="ค้นหาเนื้อหา"><div class="cmdk-in">'
      +'<svg class="ic" viewBox="0 0 24 24" style="width:18px"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>'
      +'<input type="text" placeholder="ค้นหาบทเรียนและเวิร์กช็อป..." aria-label="ค้นหา" autocomplete="off">'
      +'<kbd>esc</kbd></div><div class="cmdk-results"></div>'
      +'<div class="cmdk-foot"><span><b>↑↓</b> เลือก</span><span><b>↵</b> เปิด</span><span><b>esc</b> ปิด</span></div></div>';
    document.body.appendChild(ov);
    var input=ov.querySelector('input'), box=ov.querySelector('.cmdk-results');
    function load(){if(loaded)return;loaded=true;
      fetch(pre+'search-index.json').then(function(r){return r.json();}).then(function(j){data=j;render();}).catch(function(){data=[];render();});}
    function open(){ov.hidden=false;document.body.classList.add('cmdk-on');load();render();setTimeout(function(){input.focus();input.select();},20);}
    function close(){ov.hidden=true;document.body.classList.remove('cmdk-on');}
    function score(e,toks){var k=e.k;for(var i=0;i<toks.length;i++){if(k.indexOf(toks[i])<0)return -1;}
      var t=e.t.toLowerCase();return t.indexOf(toks[0])===0?3:(t.indexOf(toks[0])>=0?2:1);}
    function compute(){if(!data)return [];var q=input.value.trim().toLowerCase();
      if(!q)return data.slice(0,8);
      var toks=q.split(/\s+/),scored=[];
      for(var i=0;i<data.length;i++){var s=score(data[i],toks);if(s>0)scored.push([s,i,data[i]]);}
      scored.sort(function(a,b){return b[0]-a[0]||a[1]-b[1];});
      return scored.slice(0,24).map(function(x){return x[2];});}
    function setActive(i){active=i;[].forEach.call(box.querySelectorAll('.cmdk-item'),function(a,j){a.classList.toggle('active',j===i);});
      var el=box.querySelector('.cmdk-item.active');if(el)el.scrollIntoView({block:'nearest'});}
    function go(){var el=box.querySelector('.cmdk-item.active');if(el)location.href=el.getAttribute('href');}
    function render(){results=compute();active=0;
      if(!data){box.innerHTML='<div class="cmdk-empty">กำลังโหลด...</div>';return;}
      if(!results.length){box.innerHTML='<div class="cmdk-empty">ไม่พบผลลัพธ์สำหรับ "'+esc(input.value)+'"</div>';return;}
      var h='';results.forEach(function(e,i){
        h+='<a class="cmdk-item'+(i===0?' active':'')+'" href="'+pre+e.u+'" data-i="'+i+'">'
          +'<span class="ci-tag ci-'+(e.tag==='บทเรียน'?'l':'w')+'">'+esc(e.tag)+'</span>'
          +'<span class="ci-main"><span class="ci-t">'+esc(e.t)+'</span><span class="ci-g">'+esc(e.g)+'</span></span>'
          +'<svg class="ic ci-go" viewBox="0 0 24 24" style="width:15px"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>';});
      box.innerHTML=h;
      [].forEach.call(box.querySelectorAll('.cmdk-item'),function(a,i){a.addEventListener('mousemove',function(){if(active!==i)setActive(i);});});}
    input.addEventListener('input',render);
    input.addEventListener('keydown',function(e){
      if(e.key==='ArrowDown'){e.preventDefault();setActive(Math.min(active+1,results.length-1));}
      else if(e.key==='ArrowUp'){e.preventDefault();setActive(Math.max(active-1,0));}
      else if(e.key==='Enter'){e.preventDefault();go();}
      else if(e.key==='Escape'){e.preventDefault();close();}});
    ov.addEventListener('click',function(e){if(e.target===ov)close();});
    document.addEventListener('keydown',function(e){
      if((e.metaKey||e.ctrlKey)&&(e.key==='k'||e.key==='K')){e.preventDefault();if(ov.hidden)open();else close();}
      else if(e.key==='/'&&ov.hidden&&!/^(INPUT|TEXTAREA)$/.test(e.target.tagName||'')){e.preventDefault();open();}});
    var brand=document.querySelector('.sidebar .brand');
    if(brand){var b=document.createElement('button');b.type='button';b.className='sb-search';
      b.innerHTML='<svg class="ic" viewBox="0 0 24 24" style="width:16px"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg><span>ค้นหาเนื้อหา</span><kbd>'+(isMac?'⌘K':'Ctrl K')+'</kbd>';
      b.addEventListener('click',open);brand.insertAdjacentElement('afterend',b);}
    var tbh=document.querySelector('.topbar .tb-here');
    if(tbh){var t=document.createElement('button');t.type='button';t.className='tb-search';t.setAttribute('aria-label','ค้นหา');
      t.innerHTML='<svg class="ic" viewBox="0 0 24 24" style="width:19px"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>';
      t.addEventListener('click',open);tbh.parentNode.appendChild(t);}
  }

  document.addEventListener('DOMContentLoaded',function(){refresh();tabs();quiz();complete();nav();spy();initSteps();initAgentDemo();initSearch();});
})();
