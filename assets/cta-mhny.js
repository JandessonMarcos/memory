/* ============================================================================
   Memory Lab — MemoHoney offer wiring
   EDIT ONLY THE CONFIG BLOCK BELOW.
   ----------------------------------------------------------------------------
   Mirrors assets/cta.js (the Memopezil wiring) but drives a DIFFERENT offer,
   so the two never collide:
     a.buy-link       -> Memopezil   (cta.js)
     a.buy-link-mhny  -> MemoHoney   (this file)

   MemoHoney offer IDs (note they differ from Memopezil's on every field):
     account_id 12850 · aff_id 1622 · codenames PP_MMH{2,3,6}UNITS_AFF
     (Memopezil is account_id 12340 · aff_id 21099 · PP_MMP{2,3,6}UNITS_AFF)

   The {clickid} token is replaced at runtime by our subid so a sale ties back
   to the page, the package and the button position.

   Two params were deliberately stripped from the URL as supplied:
     sessid2=…  a stale session id (stamped 2026-07-23), not part of affiliate
                attribution, so carrying it forward serves no purpose
     redirect=… base64 of https://improvingourhealth.com/mmh-aff-buy-up1/,
                an upsell hop we do not want between the click and the cart

   ⚠️  VERIFICATION STATUS
     "6" was supplied directly and is confirmed.
     "2" and "3" were DERIVED from the codename pattern, which mirrors the
     Memopezil family exactly. They could not be verified programmatically:
     BuyGoods renders its checkout client-side, so a bogus codename returns a
     byte-identical 200 to a real one. Click both in a browser once and confirm
     the cart shows 2 bottles / $158 and 3 bottles / $207.
   ============================================================================ */
(function(){
  "use strict";

  var BG = "https://buygoods.com/secure/checkout.html?aff_id=1622&account_id=12850&product_codename=";
  var OFFERS = {
    "2": BG + "PP_MMH2UNITS_AFF&subid={clickid}",   // derived from pattern — click-test
    "3": BG + "PP_MMH3UNITS_AFF&subid={clickid}",   // derived from pattern — click-test
    "6": BG + "PP_MMH6UNITS_AFF&subid={clickid}"    // supplied and confirmed
  };
  var DEFAULT_PACK = "6";      // generic buttons go to best value
  var SUBID_TAG    = "mhny_g"; // base label for this offer (memohoney / google)

  var qs = new URLSearchParams(location.search);
  var incoming = qs.get('clickid') || qs.get('gclid') || qs.get('gbraid') || qs.get('wbraid')
              || qs.get('rtkcid') || qs.get('cid') || qs.get('sub1') || '';
  incoming = (incoming || '').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,60);

  function pageTag(){
    var seg = (location.pathname || '').replace(/^\/+|\/+$/g,'').split('/').pop() || 'home';
    seg = seg.toLowerCase().replace(/\.html?$/,'').replace(/[^a-z0-9-]/g,'').slice(0,40);
    return seg || 'home';
  }
  function buildHref(pack, rank){
    var url = OFFERS[pack] || OFFERS[DEFAULT_PACK];
    if(!url) return '';
    var sub = SUBID_TAG + '_' + pageTag() + '_p' + pack + '_r' + rank + (incoming ? '_' + incoming : '');
    return url.replace('{clickid}', encodeURIComponent(sub));
  }

  var pending = 0;
  document.querySelectorAll('a.buy-link-mhny').forEach(function(a){
    var pack = a.getAttribute('data-pack') || DEFAULT_PACK;
    var rank = a.getAttribute('data-rank') || '1';
    var href = buildHref(pack, rank);

    if(!href){
      // No URL configured yet: neutralise the button rather than send the click
      // to the wrong offer (or to a 404 anchor).
      pending++;
      a.removeAttribute('href');
      a.setAttribute('aria-disabled','true');
      a.classList.add('is-pending');
      a.addEventListener('click', function(e){ e.preventDefault(); });
      return;
    }

    a.setAttribute('href', href);
    a.setAttribute('target','_blank');
    a.setAttribute('rel','nofollow sponsored noopener');
    a.addEventListener('click', function(){
      var label = pageTag() + '_p' + pack + '_r' + rank;
      try{ if(window.gtag){ gtag('event','checkout_click',{event_category:'outbound',event_label:label,page_slug:pageTag(),offer:'memohoney',pack:pack,rank:rank}); } }catch(e){}
      try{ if(window.fbq){ fbq('track','InitiateCheckout',{content_name:pageTag(),content_category:'mhny_pack'+pack}); } }catch(e){}
    });
  });

  if(pending){
    try{ console.warn('[cta-mhny] '+pending+' MemoHoney button(s) disabled: no checkout URL configured in assets/cta-mhny.js'); }catch(e){}
  }
})();
