/* ============================================================================
   Memory Lab — shared CTA wiring + dates
   EDIT ONLY THE CONFIG BLOCK.
   ----------------------------------------------------------------------------
   OFFERS : real BuyGoods checkout links per package (2 / 3 / 6 bottles).
            The {clickid} token is replaced at runtime by our subid so the sale
            ties back to the source/keyword/campaign and the CTA position.
   How tracking flows:
     - Any incoming click id from your ad (?clickid= / ?rtkcid= / ?cid= / ?sub1=)
       is forwarded inside the subid.
     - subid format: mem_g_p{pack}_r{rank}[_{incoming}]
       p = package (2/3/6), r = on-page position (rank1..rank5).
   How to wire a button in the HTML:
     - <a class="buy-link" data-pack="6"> -> goes to the 6-bottle checkout
     - <a class="buy-link" data-rank="1"> (no data-pack) -> DEFAULT_PACK below
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

  var OFFERS = {
    "2": "https://buygoods.com/secure/checkout.html?account_id=12340&product_codename=PP_MMP2UNITS_AFF&aff_id=21099&subid={clickid}&redirect=aHR0cHM6Ly9pbXByb3ZpbmdvdXJoZWFsdGguY29tL21tcC1hZmYtYnV5LXVwMS8=&sub5=redirect_test",
    "3": "https://buygoods.com/secure/checkout.html?account_id=12340&product_codename=PP_MMP3UNITS_AFF&aff_id=21099&subid={clickid}&redirect=aHR0cHM6Ly9pbXByb3ZpbmdvdXJoZWFsdGguY29tL21tcC1hZmYtYnV5LXVwMS8=&sub5=redirect_test",
    "6": "https://buygoods.com/secure/checkout.html?account_id=12340&product_codename=PP_MMP6UNITS_AFF&aff_id=21099&subid={clickid}&redirect=aHR0cHM6Ly9pbXByb3ZpbmdvdXJoZWFsdGguY29tL21tcC1hZmYtYnV5LXVwMS8=&sub5=redirect_test"
  };
  var DEFAULT_PACK = "6";     // generic "See Today's Price" buttons go to best value
  var SUBID_TAG    = "mem_g"; // base label for this site/source (memory / google)

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
  function buildHref(pack, rank){
    var url = OFFERS[pack] || OFFERS[DEFAULT_PACK];
    var sub = SUBID_TAG + '_' + pageTag() + '_p' + pack + '_r' + rank + (incoming ? '_' + incoming : '');
    return url.replace('{clickid}', encodeURIComponent(sub));
  }
  document.querySelectorAll('a.buy-link').forEach(function(a){
    var href = a.getAttribute('href') || '';
    if(href.length > 1 && href.charAt(0) === '#') return;   // leave real in-page anchors (#offer) alone
    var pack = a.getAttribute('data-pack') || DEFAULT_PACK;
    var rank = a.getAttribute('data-rank') || '1';
    a.setAttribute('href', buildHref(pack, rank));
    a.setAttribute('target','_blank');
    a.setAttribute('rel','nofollow sponsored noopener');
    // Proxy conversion: the real sale happens off-site on BuyGoods, so fire an
    // "outbound checkout click" into GA4 + Meta. This is the event Google Ads /
    // Meta optimize toward when you buy traffic. Label carries page+pack+rank.
    a.addEventListener('click', function(){
      var label = pageTag() + '_p' + pack + '_r' + rank;
      try{ if(window.gtag){ gtag('event','checkout_click',{event_category:'outbound',event_label:label,page_slug:pageTag(),pack:pack,rank:rank}); } }catch(e){}
      try{ if(window.fbq){ fbq('track','InitiateCheckout',{content_name:pageTag(),content_category:'pack'+pack}); } }catch(e){}
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
