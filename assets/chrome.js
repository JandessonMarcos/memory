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
  var as=document.querySelector('.ml-aside');
  if(as){
    fetch('/assets/latest.json').then(function(r){return r.json();}).then(function(L){
      var here=location.pathname, h='<div class="as-in"><h3>Latest</h3>';
      L.filter(function(x){return x.u!==here;}).slice(0,6).forEach(function(x){
        var e=function(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
        h+='<a href="'+x.u+'">'+(x.i?'<img src="'+x.i+'" alt="" loading="lazy" width="84" height="84">':'')+'<div><span>'+e(x.c)+'</span><b>'+e(x.t)+'</b></div></a>';
      });
      as.innerHTML=h+'</div>';
    }).catch(function(){});
  }
})();
