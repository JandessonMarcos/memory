(function(){
  var b=document.querySelector('.mlh-menu'), nav=document.querySelector('.mlh-nav-in');
  if(b&&nav){
    var d=document.createElement('div'); d.className='mld';
    d.innerHTML='<nav aria-label="Menu">'+nav.innerHTML+'</nav>';
    document.body.appendChild(d);
    b.addEventListener('click',function(){ d.classList.add('open'); b.setAttribute('aria-expanded','true'); });
    d.addEventListener('click',function(e){ if(e.target===d){ d.classList.remove('open'); b.setAttribute('aria-expanded','false'); } });
  }
  if(nav){
    var p=location.pathname, m=p.match(/^\/topics\/[^\/]+\//);
    [].forEach.call(nav.querySelectorAll('a'),function(a){ var h=a.getAttribute('href'); if((m&&h===m[0])||(p==='/'&&h==='/')) a.classList.add('on'); });
  }
  // home hero: reveal extra stories while they fit beside the lead column
  var hx=document.querySelector('.hx');
  function fill(){
    if(!hx) return;
    var a=hx.querySelector('.hx-a'); if(!a) return;
    [['.hx-b','.st',3],['.hx-c','.th',5]].forEach(function(c){
      var col=hx.querySelector(c[0]); if(!col) return;
      var items=col.querySelectorAll(c[1]);
      for(var i=c[2];i<items.length;i++) items[i].classList.remove('show');
      if(window.innerWidth<=1280&&c[0]==='.hx-c') return;
      if(window.innerWidth<=760) return;
      var limit=a.getBoundingClientRect().bottom;
      for(var j=c[2];j<items.length;j++){
        items[j].classList.add('show');
        if(items[j].getBoundingClientRect().bottom>limit+4){ items[j].classList.remove('show'); break; }
      }
    });
  }
  if(hx){ fill(); window.addEventListener('load',fill); var t; window.addEventListener('resize',function(){ clearTimeout(t); t=setTimeout(fill,150); }); }

  // left rail: table of contents from the article's section headings
  var toc=document.querySelector('.ml-toc'), art=document.querySelector('article.article');
  if(toc&&art){
    var hs=art.querySelectorAll('h2.sec'), links=[];
    if(hs.length>1){
      var h='<div class="toc-in"><h3>In this article</h3>';
      [].forEach.call(hs,function(el,i){ if(!el.id) el.id='s'+(i+1); h+='<a href="#'+el.id+'">'+el.textContent.replace(/[&<>]/g,'')+'</a>'; });
      toc.innerHTML=h+'</div>'; links=toc.querySelectorAll('a');
      var spy=function(){ var cur=-1; [].forEach.call(hs,function(el,i){ if(el.getBoundingClientRect().top<160) cur=i; }); [].forEach.call(links,function(l,i){ l.classList.toggle('on',i===cur); }); };
      window.addEventListener('scroll',spy,{passive:true}); spy();
    }
  }

  var as=document.querySelector('.ml-aside');
  if(as){
    fetch('/assets/latest.json').then(function(r){return r.json();}).then(function(L){
      var here=location.pathname, h='<div class="as-in"><h3>Latest</h3>';
      L.filter(function(x){return x.u!==here;}).slice(0,6).forEach(function(x){
        var e=function(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
        h+='<a href="'+x.u+'">'+(x.i?'<img src="'+x.i+'" alt="" loading="lazy" width="84" height="84">':'')+'<div><span>'+e(x.c)+'</span><b>'+e(x.t)+'</b></div></a>';
      });
      h+='<a class="promo" href="/memory-test/"><div><b>How sharp is your memory?</b><span>Two quick tasks, a score in 3 minutes. Free, no sign-up.</span><i>Take the free test</i></div></a>';
      var pop=[['/how-to-improve-memory/','How to Improve Your Memory: 11 Science-Backed Ways'],['/brain-fog-causes-and-fixes/','Brain Fog: 7 Common Causes and How to Clear It'],['/sleep-and-memory/','Sleep and Memory: Why Deep Sleep Locks In Recall'],['/best-memory-supplements-2026/','The 5 Best Memory Formulas of 2026']];
      h+='<h3 class="pop">Most read</h3><div class="poplist">';
      pop.filter(function(x){return x[0]!==here;}).forEach(function(x,i){ h+='<a href="'+x[0]+'"><em>'+(i+1)+'</em><div><b>'+x[1]+'</b></div></a>'; });
      as.innerHTML=h+'</div></div>';
    }).catch(function(){});
  }
})();
