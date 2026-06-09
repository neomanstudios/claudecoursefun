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

  window.cp=function(){var el=document.getElementById('pt');if(!el)return;navigator.clipboard.writeText(el.innerText);
    var b=document.querySelector('.copy-btn');if(!b)return;var o=b.innerHTML;b.innerHTML='คัดลอกแล้ว';b.classList.add('done');
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

  document.addEventListener('DOMContentLoaded',function(){refresh();tabs();quiz();complete();nav();spy();});
})();
