/* ============================================================================
   Memory Lab — "Memory Check" quiz + lead capture (site-wide)
   ----------------------------------------------------------------------------
   Surfaces:
     1) INLINE  — any page that has <div id="mlq-mount"> (the buyer's guide).
     2) FLOATING BUTTON — every other page (loaded via cta.js): a small
        "Memory Check" FAB that opens the quiz in a modal.
     3) EXIT-INTENT — desktop: when the mouse leaves toward the top, the modal
        opens once per session (skipped if the visitor already submitted).
   Capture: POST /api/lead -> D1. Fails open (never blocks the visitor). The
   result routes to the #1 offer carrying the lead subid (quiz_<id>_<segment>),
   so a later BuyGoods sale ties back to this exact lead.
   EDIT ONLY THE CONFIG BLOCK.
   ============================================================================ */
(function () {
  "use strict";

  // ----------------------------- CONFIG ------------------------------------
  var CFG = {
    endpoint: "/api/lead",
    offerPath: "/best-memory-supplements-2026/",
    offerAnchor: "#pick",
    subidBase: "quiz",
    privacyUrl: "/about/"
  };

  var STEPS = [
    { key: "symptom", q: "What bothers you most right now?", opts: [
      { v: "names", emoji: "🗣️", label: "Forgetting names &amp; words" },
      { v: "focus", emoji: "🧩", label: "Losing my train of thought" },
      { v: "fog",   emoji: "🌫️", label: "Afternoon brain fog" },
      { v: "multi", emoji: "🔀", label: "Trouble juggling tasks" }
    ]},
    { key: "age", q: "Which age range are you in?", opts: [
      { v: "u45", emoji: "", label: "Under 45" },
      { v: "45",  emoji: "", label: "45 – 54" },
      { v: "55",  emoji: "", label: "55 – 64" },
      { v: "65",  emoji: "", label: "65 or older" }
    ]},
    { key: "dur", q: "How long has it been going on?", opts: [
      { v: "new",  emoji: "", label: "Just recently (weeks)" },
      { v: "mo",   emoji: "", label: "A few months" },
      { v: "yr",   emoji: "", label: "A year or more" },
      { v: "prev", emoji: "", label: "Not really, I just want to stay sharp" }
    ]},
    { key: "tried", q: "Have you tried a memory supplement before?", opts: [
      { v: "no",   emoji: "", label: "Never" },
      { v: "fail", emoji: "", label: "Yes, it did nothing" },
      { v: "some", emoji: "", label: "Yes, some help" },
      { v: "now",  emoji: "", label: "I'm taking one now" }
    ]}
  ];

  var MATCH = {
    names: "a transparent, clinically-dosed citicoline + bacopa formula",
    focus: "a focus-first formula with citicoline at a clinical dose",
    fog:   "a formula that pairs B-vitamins with citicoline for afternoon fog",
    multi: "a full-spectrum formula with phosphatidylserine + citicoline"
  };

  // ----------------------------- UTIL --------------------------------------
  function track(name, params) { try { if (window.gtag) gtag("event", name, params || {}); } catch (e) {} }
  function genId() { var t = Date.now().toString(36); var r = (Math.floor(Math.random() * 1e6)).toString(36); return (t + r).slice(-9); }
  function escapeHtml(s) { return String(s).replace(/[<>&"]/g, function (c) { return { "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" }[c]; }); }
  function setDone() { try { sessionStorage.setItem("mlq_done", "1"); } catch (e) {} hideFab(); }
  function isDone() { try { return sessionStorage.getItem("mlq_done") === "1"; } catch (e) { return false; } }
  function hideFab() { var f = document.querySelector(".mlq-fab"); if (f) f.style.display = "none"; }

  // ----------------------- QUIZ INSTANCE (own state) -----------------------
  function createQuiz(mount) {
    var answers = {}, idx = 0, leadId = genId();

    function progress() {
      var pct = Math.round((idx / (STEPS.length + 1)) * 100);
      return '<div class="mlq-prog"><div class="mlq-prog-bar" style="width:' + pct + '%"></div></div>';
    }

    function renderStep() {
      var s = STEPS[idx];
      var html = progress() + '<div class="mlq-step"><p class="mlq-q">' + (idx + 1) + ". " + s.q + "</p><div class='mlq-opts'>";
      s.opts.forEach(function (o) {
        var em = o.emoji ? '<span class="emoji">' + o.emoji + "</span>" : '<span class="dot"></span>';
        html += '<button type="button" class="mlq-opt" data-v="' + o.v + '">' + em + "<span>" + o.label + "</span></button>";
      });
      html += "</div>";
      if (idx > 0) html += '<button type="button" class="mlq-back" data-back="1">&larr; Back</button>';
      html += "</div>";
      mount.innerHTML = html;
      mount.querySelectorAll(".mlq-opt").forEach(function (b) {
        b.addEventListener("click", function () {
          answers[s.key] = b.getAttribute("data-v");
          track("quiz_answer", { step: s.key, value: answers[s.key] });
          idx++;
          idx < STEPS.length ? renderStep() : renderGate();
        });
      });
      var back = mount.querySelector("[data-back]");
      if (back) back.addEventListener("click", function () { idx--; renderStep(); });
    }

    function renderGate() {
      track("quiz_complete", { segment: segment() });
      mount.innerHTML = progress() +
        '<div class="mlq-step mlq-gate">' +
          '<div class="lock">🧠</div>' +
          "<h3>Your Memory Action Plan is ready</h3>" +
          "<p>Enter your email and we'll show your result now and send your personalized plan + our #1 rated formula for your situation.</p>" +
          '<form class="mlq-form" novalidate>' +
            '<input type="text" class="mlq-hp" tabindex="-1" autocomplete="off" name="website" aria-hidden="true">' +
            '<input type="email" inputmode="email" autocomplete="email" placeholder="you@email.com" required>' +
            '<button type="submit" class="mlq-btn">Show my result &rarr;</button>' +
            '<div class="mlq-err" role="alert"></div>' +
          "</form>" +
          '<p class="mlq-fine">We respect your privacy. Unsubscribe anytime. No spam, just your plan and occasional brain-health tips. <a href="' + CFG.privacyUrl + '">Privacy</a>.</p>' +
          '<button type="button" class="mlq-back" data-back="1">&larr; Back</button>' +
        "</div>";
      var form = mount.querySelector(".mlq-form");
      var err = mount.querySelector(".mlq-err");
      mount.querySelector("[data-back]").addEventListener("click", function () { idx = STEPS.length - 1; renderStep(); });
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (form.website.value) return;
        var email = form.querySelector("input[type=email]").value.trim();
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { err.textContent = "Please enter a valid email."; return; }
        var btn = form.querySelector(".mlq-btn");
        btn.disabled = true; btn.textContent = "Getting your result…"; err.textContent = "";
        submitLead(email, function () { renderResult(email); });
      });
    }

    function renderResult(email) {
      var sym = answers.symptom || "focus";
      var subid = CFG.subidBase + "_" + leadId + "_" + segment();
      var url = CFG.offerPath + "?clickid=" + encodeURIComponent(subid) + CFG.offerAnchor;
      track("quiz_lead", { segment: segment() });
      setDone();
      mount.innerHTML =
        '<div class="mlq-step mlq-result">' +
          '<span class="badge">★ Your match</span>' +
          "<h3>Based on your answers, look for <span class='match'>" + (MATCH[sym] || MATCH.focus) + "</span>.</h3>" +
          "<p>That's exactly the profile of the formula our editors rated <strong>#1 for 2026</strong>: fully transparent label, clinical doses, and a 60-day guarantee. Here's where to see it:</p>" +
          '<a class="mlq-btn" href="' + url + '" rel="nofollow sponsored">See your #1 match &rarr;</a>' +
          '<p class="sent">✓ Plan sent to ' + escapeHtml(email) + "</p>" +
        "</div>";
    }

    function segment() {
      return ["s" + (answers.symptom || ""), "a" + (answers.age || ""), "d" + (answers.dur || ""), "t" + (answers.tried || "")].join("");
    }

    function submitLead(email, cb) {
      var qs = new URLSearchParams(location.search);
      var payload = {
        email: email, lead_id: leadId, subid: CFG.subidBase + "_" + leadId + "_" + segment(),
        answers: answers, segment: segment(), source_page: location.pathname,
        referrer: document.referrer || "",
        incoming_clickid: qs.get("clickid") || qs.get("rtkcid") || qs.get("cid") || qs.get("sub1") || "",
        utm: { source: qs.get("utm_source") || "", medium: qs.get("utm_medium") || "", campaign: qs.get("utm_campaign") || "" },
        consent: true
      };
      var finished = false; function finish() { if (!finished) { finished = true; cb(); } }
      try {
        fetch(CFG.endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), keepalive: true })
          .then(function () {}).catch(function () {}).finally(finish);
      } catch (e) { finish(); }
      setTimeout(finish, 2500);
    }

    track("quiz_view", {});
    renderStep();
  }

  // ----------------------------- SURFACES ----------------------------------
  function boot() {
    var inline = document.getElementById("mlq-mount");
    if (inline) createQuiz(inline);          // inline lives on the buyer's guide
    if (!isDone()) buildSiteWide(!!inline);  // FAB (skip if inline present) + exit-intent + modal
  }

  function buildSiteWide(hasInline) {
    // modal (used by FAB + exit-intent)
    var modal = document.createElement("div");
    modal.className = "mlq-modal";
    modal.setAttribute("aria-hidden", "true");
    modal.innerHTML =
      '<div class="mlq-modal-card" role="dialog" aria-modal="true">' +
        '<button class="mlq-modal-x" aria-label="Close">&times;</button>' +
        '<span class="mlq-kicker">★ Free 60-second tool</span>' +
        '<h2 class="mlq-title">Not sure which approach fits <em>you</em>?</h2>' +
        '<p class="mlq-sub">Answer 4 quick questions and get your personalized Memory Action Plan plus our #1 rated formula for your situation.</p>' +
        '<div class="mlq-modal-mount"></div>' +
      "</div>";
    document.body.appendChild(modal);
    var mountEl = modal.querySelector(".mlq-modal-mount");
    var built = false;
    function open() {
      if (isDone()) return;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      if (!built) { createQuiz(mountEl); built = true; }
      track("quiz_open", {});
    }
    function close() { modal.classList.remove("open"); modal.setAttribute("aria-hidden", "true"); }
    modal.querySelector(".mlq-modal-x").addEventListener("click", close);
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    // floating button (only on pages without the inline quiz, to avoid redundancy)
    if (!hasInline) {
      var btn = document.createElement("button");
      btn.className = "mlq-fab"; btn.type = "button";
      btn.innerHTML = '<span class="mlq-fab-ic">🧠</span><span class="mlq-fab-tx">Memory Check<small>Free 60-sec quiz</small></span>';
      document.body.appendChild(btn);
      btn.addEventListener("click", open);
      setTimeout(function () { btn.classList.add("show"); }, 1200);
    }

    // exit-intent (desktop): pointer leaves toward the top of the viewport
    var exitShown = false;
    document.addEventListener("mouseout", function (e) {
      if (exitShown || isDone()) return;
      if (e.clientY <= 0 && !e.relatedTarget) { exitShown = true; open(); }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
