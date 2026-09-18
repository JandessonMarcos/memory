/* ============================================================================
   Offer bridge page — checkout wiring, countdown, sticky bar
   EDIT ONLY THE OFFERS BLOCK.
   ----------------------------------------------------------------------------
   These pages sit between a blog CTA and the BuyGoods cart. A reader clicks a
   post's button, lands here, picks a package, and only THEN goes to checkout.

   Attribution has to survive that extra hop, so the blog's CTA scripts hand the
   click over in the query string instead of building the subid themselves:

       /go/memopezil/?s=<post-slug>&r=<button-rank>&c=<incoming-clickid>

   This file reassembles the subid in the SAME format the blog used to send
   straight to BuyGoods, so existing reports keep working:

       <tag>_<post-slug>_p<pack>_r<rank>[_<incoming>]

   The one change: p<pack> is now the package the reader actually chose here,
   not the guess the blog button had to make.

   If someone lands here with no query string (typed the URL, shared link), the
   subid degrades to <tag>_direct_p<pack>_r0 — still a valid, traceable sale.
   ============================================================================ */
(function () {
  "use strict";

  var OFFERS = {
    // MemoPezil — account_id 12340 · aff_id 21099
    mepz: {
      tag: "mem_g",
      name: "memopezil",
      packs: {
        "2": "https://buygoods.com/secure/checkout.html?account_id=12340&product_codename=PP_MMP2UNITS_AFF&aff_id=21099&subid={clickid}&redirect=aHR0cHM6Ly9pbXByb3ZpbmdvdXJoZWFsdGguY29tL21tcC1hZmYtYnV5LXVwMS8=&sub5=redirect_test",
        "3": "https://buygoods.com/secure/checkout.html?account_id=12340&product_codename=PP_MMP3UNITS_AFF&aff_id=21099&subid={clickid}&redirect=aHR0cHM6Ly9pbXByb3ZpbmdvdXJoZWFsdGguY29tL21tcC1hZmYtYnV5LXVwMS8=&sub5=redirect_test",
        "6": "https://buygoods.com/secure/checkout.html?account_id=12340&product_codename=PP_MMP6UNITS_AFF&aff_id=21099&subid={clickid}&redirect=aHR0cHM6Ly9pbXByb3ZpbmdvdXJoZWFsdGguY29tL21tcC1hZmYtYnV5LXVwMS8=&sub5=redirect_test"
      }
    },
    // MemoHoney — account_id 12850 · aff_id 1622
    // "6" was supplied and confirmed; "2" and "3" follow the codename pattern
    // and still need one click-test each (BuyGoods returns 200 for a bad
    // codename, so a bogus one cannot be caught programmatically).
    mhny: {
      tag: "mhny_g",
      name: "memohoney",
      packs: {
        "2": "https://buygoods.com/secure/checkout.html?aff_id=1622&account_id=12850&product_codename=PP_MMH2UNITS_AFF&subid={clickid}",
        "3": "https://buygoods.com/secure/checkout.html?aff_id=1622&account_id=12850&product_codename=PP_MMH3UNITS_AFF&subid={clickid}",
        "6": "https://buygoods.com/secure/checkout.html?aff_id=1622&account_id=12850&product_codename=PP_MMH6UNITS_AFF&subid={clickid}"
      }
    }
  };

  var DEFAULT_PACK = "6";
  var TIMER_MINUTES = 30;

  var brand = document.documentElement.getAttribute("data-brand") || "";
  var offer = OFFERS[brand];
  if (!offer) {
    try { console.error('[offer] unknown data-brand="' + brand + '"'); } catch (e) {}
    return;
  }

  // ---- where this click came from -----------------------------------------
  function clean(v, max) {
    return (v || "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, max);
  }
  var qs = new URLSearchParams(location.search);
  var srcPage = clean(qs.get("s"), 40) || "direct";
  var srcRank = clean(qs.get("r"), 2) || "0";
  // Accept a raw ad click id too, in case this page is ever used as a direct
  // ad destination rather than only as a step after the blog.
  var incoming = clean(
    qs.get("c") || qs.get("clickid") || qs.get("gclid") || qs.get("gbraid") ||
    qs.get("wbraid") || qs.get("rtkcid") || qs.get("cid") || qs.get("sub1"), 60
  );

  function buildHref(pack) {
    var url = offer.packs[pack] || offer.packs[DEFAULT_PACK];
    if (!url) return "";
    var sub = offer.tag + "_" + srcPage + "_p" + pack + "_r" + srcRank +
              (incoming ? "_" + incoming : "");
    return url.replace("{clickid}", encodeURIComponent(sub));
  }

  // ---- wire every checkout button ------------------------------------------
  var pending = 0;
  document.querySelectorAll("a.js-checkout").forEach(function (a) {
    var pack = a.getAttribute("data-pack") || DEFAULT_PACK;
    var href = buildHref(pack);

    if (!href) {
      // Neutralise rather than send the click to the wrong cart.
      pending++;
      a.removeAttribute("href");
      a.setAttribute("aria-disabled", "true");
      a.classList.add("is-pending");
      a.addEventListener("click", function (e) { e.preventDefault(); });
      return;
    }

    a.setAttribute("href", href);
    a.setAttribute("rel", "nofollow sponsored noopener");
    a.addEventListener("click", function () {
      var label = srcPage + "_p" + pack + "_r" + srcRank;
      try {
        if (window.gtag) {
          gtag("event", "checkout_click", {
            event_category: "outbound", event_label: label,
            page_slug: srcPage, offer: offer.name, pack: pack, rank: srcRank
          });
        }
      } catch (e) {}
      try {
        if (window.fbq) {
          fbq("track", "InitiateCheckout", {
            content_name: srcPage, content_category: offer.name + "_pack" + pack
          });
        }
      } catch (e) {}
    });
  });
  if (pending) {
    try { console.warn("[offer] " + pending + " button(s) disabled: no checkout URL for this pack"); } catch (e) {}
  }

  // ---- countdown -----------------------------------------------------------
  // Anchored in sessionStorage so it counts the visit, not the scroll position:
  // every timer on the page shows the same number and a refresh does not hand
  // the reader a fresh 30 minutes.
  (function () {
    var els = document.querySelectorAll(".js-timer");
    if (!els.length) return;

    var KEY = "offer_deadline_" + brand;
    var deadline = 0;
    try { deadline = parseInt(sessionStorage.getItem(KEY) || "0", 10); } catch (e) {}
    var now = Date.now();
    if (!deadline || deadline <= now || deadline > now + TIMER_MINUTES * 60000) {
      deadline = now + TIMER_MINUTES * 60000;
      try { sessionStorage.setItem(KEY, String(deadline)); } catch (e) {}
    }

    function pad(n) { return n < 10 ? "0" + n : String(n); }
    function tick() {
      var left = Math.max(0, deadline - Date.now());
      var total = Math.floor(left / 1000);
      var txt = pad(Math.floor(total / 60)) + ":" + pad(total % 60);
      for (var i = 0; i < els.length; i++) els[i].textContent = txt;
      if (left <= 0) clearInterval(iv);
    }
    tick();
    var iv = setInterval(tick, 1000);
  })();

  // ---- sticky mobile bar ---------------------------------------------------
  // Only mark the body once the bar is actually on screen, so desktop does not
  // get dead space at the bottom.
  (function () {
    var bar = document.querySelector(".stickybar");
    if (!bar) return;
    function sync() {
      var on = getComputedStyle(bar).display !== "none";
      document.body.classList.toggle("has-sticky", on);
    }
    sync();
    window.addEventListener("resize", sync);
  })();

  // ---- year ----------------------------------------------------------------
  var yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();
})();
