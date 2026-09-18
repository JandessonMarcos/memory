/* ============================================================================
   Memory Lab — shared CTA wiring + dates
   EDIT ONLY THE CONFIG BLOCK.
   ----------------------------------------------------------------------------
   Buttons no longer jump straight to BuyGoods. They send the reader to the
   Memopezil offer page at /go/memopezil/, where the package is actually chosen;
   that page builds the checkout link. The real checkout URLs therefore live in
   ONE place now — assets/offer.js — instead of being duplicated here.

   How tracking flows:
     - Any incoming click id from your ad (?clickid= / ?gclid= / ?rtkcid= / …)
       is handed to the offer page as ?c=, and ends up inside the BuyGoods subid
       exactly as before.
     - The post slug goes over as ?s= and the button position as ?r=, so the
       final subid keeps its old shape: mem_g_{slug}_p{pack}_r{rank}[_{incoming}]
       The one difference: p{pack} is now the package the reader really picked.
   How to wire a button in the HTML:
     - <a class="buy-link" data-rank="1"> -> offer page, tagged as position 1
     - data-pack is no longer read here (the offer page owns that choice)
     - href="#offer" (real in-page anchor) is left untouched.
   ============================================================================ */
(function(){
  "use strict";

  // Load the "Memory Check" quiz (lead capture) site-wide — one place, every page.
  // Absolute /assets/ paths so it works from the home and from any post subfolder.
  (function(){
    try{
      if(!document.querySelector('link[href*="quiz.css"]')){
        var l=document.createElement('link'); l.rel='stylesheet'; l.href='/assets/quiz.css'; document.head.appendChild(l);
      }
      if(!document.querySelector('script[src*="quiz.js"]')){
        var s=document.createElement('script'); s.src='/assets/quiz.js'; s.defer=true; document.body.appendChild(s);
      }
    }catch(e){}
  })();

  var BRIDGE = "/go/memopezil/";  // offer page; checkout URLs live in assets/offer.js

  // ---- dates ----
  var y = new Date().getFullYear();
  ["yr"].forEach(function(id){ var el=document.getElementById(id); if(el) el.textContent=y; });

  // ---- offer links ----
  var qs = new URLSearchParams(location.search);
  // Incoming paid click id. Google Ads passes gclid (or gbraid/wbraid on some
  // Display/Discovery/iOS placements) — capture those too so paid clicks flow
  // into the BuyGoods subid and tie a sale back to the campaign.
  var incoming = qs.get('clickid') || qs.get('gclid') || qs.get('gbraid') || qs.get('wbraid')
              || qs.get('rtkcid') || qs.get('cid') || qs.get('sub1') || '';
  incoming = (incoming || '').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,60);
  // Which post the click came from: derived automatically from the URL slug so
  // every page (existing + future) self-attributes with no per-post edits.
  // "/how-to-learn-faster/" -> "how-to-learn-faster"; home "/" -> "home".
  function pageTag(){
    var seg = (location.pathname || '').replace(/^\/+|\/+$/g,'').split('/').pop() || 'home';
    seg = seg.toLowerCase().replace(/\.html?$/,'').replace(/[^a-z0-9-]/g,'').slice(0,40);
    return seg || 'home';
  }
  function buildHref(rank){
    var q = 's=' + encodeURIComponent(pageTag()) + '&r=' + encodeURIComponent(rank);
    if(incoming) q += '&c=' + encodeURIComponent(incoming);
    return BRIDGE + '?' + q;
  }
  document.querySelectorAll('a.buy-link').forEach(function(a){
    var href = a.getAttribute('href') || '';
    if(href.length > 1 && href.charAt(0) === '#') return;   // leave real in-page anchors (#offer) alone
    var rank = a.getAttribute('data-rank') || '1';
    a.setAttribute('href', buildHref(rank));
    a.removeAttribute('target');          // same tab: the offer page is a step in our own funnel
    a.setAttribute('rel','nofollow');     // internal, and the offer page is noindex anyway
    // Mid-funnel event. The checkout_click / InitiateCheckout pair now fires on
    // the offer page, at the moment the reader actually leaves for BuyGoods —
    // firing it here too would double-count and skew what Ads optimizes toward.
    a.addEventListener('click', function(){
      var label = pageTag() + '_r' + rank;
      try{ if(window.gtag){ gtag('event','offer_page_click',{event_category:'funnel',event_label:label,page_slug:pageTag(),offer:'memopezil',rank:rank}); } }catch(e){}
      try{ if(window.fbq){ fbq('track','ViewContent',{content_name:pageTag(),content_category:'memopezil_offer'}); } }catch(e){}
    });
  });

  // ---- site search (magnifier) ----
  var IDX=null;
  function loadIndex(){ if(IDX!==null) return; fetch('/assets/search-index.json').then(function(r){return r.json();}).then(function(d){IDX=d;render(document.getElementById('mlSearchInput'));}).catch(function(){IDX=[];}); }
  function esc(e){ if(e.key==='Escape') closeSearch(); }
  function closeSearch(){ var w=document.getElementById('mlSearch'); if(w) w.remove(); document.removeEventListener('keydown',esc); }
  function render(inp){
    var box=document.getElementById('mlSearchResults'); if(!box||!inp) return;
    var q=(inp.value||'').trim().toLowerCase();
    if(!q){ box.innerHTML=''; return; }
    if(IDX===null){ box.innerHTML='<div class="mls-empty">Loading…</div>'; return; }
    var hits=IDX.filter(function(it){ return (it.t+' '+(it.c||'')+' '+(it.k||'')).toLowerCase().indexOf(q)>-1; }).slice(0,8);
    box.innerHTML = hits.length ? hits.map(function(it){ return '<a href="'+it.u+'">'+it.t+'<span>'+(it.c||'')+'</span></a>'; }).join('') : '<div class="mls-empty">No results for "'+q.replace(/[<>&]/g,'')+'"</div>';
  }
  function openSearch(){
    if(document.getElementById('mlSearch')){ document.getElementById('mlSearchInput').focus(); return; }
    var w=document.createElement('div'); w.id='mlSearch';
    w.innerHTML='<div class="mls-box"><input id="mlSearchInput" type="search" placeholder="Search memory, brain fog, supplements…" autocomplete="off"><div id="mlSearchResults"></div></div>';
    document.body.appendChild(w);
    w.addEventListener('click',function(e){ if(e.target===w) closeSearch(); });
    document.addEventListener('keydown',esc);
    var inp=document.getElementById('mlSearchInput');
    inp.addEventListener('input',function(){ render(inp); });
    inp.focus(); loadIndex();
  }
  var sb=document.querySelector('.ico-search');
  if(sb) sb.addEventListener('click', function(e){ e.preventDefault(); openSearch(); });
})();
