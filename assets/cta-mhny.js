/* ============================================================================
   Memory Lab — MemoHoney offer wiring
   ----------------------------------------------------------------------------
   Mirrors assets/cta.js (the Memopezil wiring) but drives a DIFFERENT offer,
   so the two never collide:
     a.buy-link       -> Memopezil   (cta.js       -> /go/memopezil/)
     a.buy-link-mhny  -> MemoHoney   (this file    -> /go/memohoney/)

   Buttons no longer jump straight to BuyGoods. They send the reader to the
   MemoHoney offer page, where the package is actually chosen; that page builds
   the checkout link. The MemoHoney checkout URLs (account_id 12850 · aff_id
   1622 · PP_MMH{2,3,6}UNITS_AFF) therefore live in ONE place now:
   assets/offer.js.

   The post slug goes over as ?s=, the button position as ?r= and any incoming
   ad click id as ?c=, so the final BuyGoods subid keeps its old shape:
     mhny_g_{slug}_p{pack}_r{rank}[_{incoming}]
   ============================================================================ */
(function(){
  "use strict";

  var BRIDGE = "/go/memohoney/";  // offer page; checkout URLs live in assets/offer.js

  var qs = new URLSearchParams(location.search);
  var incoming = qs.get('clickid') || qs.get('gclid') || qs.get('gbraid') || qs.get('wbraid')
              || qs.get('rtkcid') || qs.get('cid') || qs.get('sub1') || '';
  incoming = (incoming || '').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,60);

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

  document.querySelectorAll('a.buy-link-mhny').forEach(function(a){
    var href = a.getAttribute('href') || '';
    if(href.length > 1 && href.charAt(0) === '#') return;   // leave real in-page anchors alone
    var rank = a.getAttribute('data-rank') || '1';
    a.setAttribute('href', buildHref(rank));
    a.removeAttribute('target');          // same tab: the offer page is a step in our own funnel
    a.setAttribute('rel','nofollow');     // internal, and the offer page is noindex anyway
    // Mid-funnel event. checkout_click / InitiateCheckout fire on the offer
    // page, at the moment the reader actually leaves for BuyGoods.
    a.addEventListener('click', function(){
      var label = pageTag() + '_r' + rank;
      try{ if(window.gtag){ gtag('event','offer_page_click',{event_category:'funnel',event_label:label,page_slug:pageTag(),offer:'memohoney',rank:rank}); } }catch(e){}
      try{ if(window.fbq){ fbq('track','ViewContent',{content_name:pageTag(),content_category:'memohoney_offer'}); } }catch(e){}
    });
  });
})();
