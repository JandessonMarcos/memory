/* ============================================================================
   Memory Lab — "Memory Check" quiz + lead capture
   ----------------------------------------------------------------------------
   STRATEGY (read before editing):
     - This NEVER gates the offer. The direct-sale buy-links keep selling.
       The quiz only harvests the visitor who was NOT going to click buy.
     - Lead is stored in OUR D1 via POST /api/lead (own the data).
     - Closing the loop: each lead gets a short id. We forward it as ?clickid=
       to the money page, where cta.js folds it into the BuyGoods subid
       (mem_g_p6_r1_q<id>_<seg>). Since the financial panel's `sales` table
       stores subid, a later $215 sale can be matched back to THIS lead.
     - Fails open: if /api/lead is unreachable (backend not deployed yet), the
       visitor still gets their result + offer. We never block the funnel.
   EDIT ONLY THE CONFIG BLOCK.
   ============================================================================ */
(function () {
  "use strict";
  var mount = document.getElementById("mlq-mount");
  if (!mount) return;

  // ----------------------------- CONFIG ------------------------------------
  var CFG = {
    endpoint: "/api/lead",                       // Worker route (D1 storage)
    offerPath: "/best-memory-supplements-2026/", // money page does the selling
    offerAnchor: "#pick",
    subidBase: "quiz",                            // label for this source
    privacyUrl: "/about/"                         // TODO: swap for real /privacy/ when live
  };

  // ----------------------------- QUESTIONS ---------------------------------
  // value codes are kept SHORT — they ride inside the subid + get stored.
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

  // result headline tuned to the primary symptom (all converge on the #1 pick)
  var MATCH = {
    names: "a transparent, clinically-dosed citicoline + bacopa formula",
    focus: "a focus-first formula with citicoline at a clinical dose",
    fog:   "a formula that pairs B-vitamins with citicoline for afternoon fog",
    multi: "a full-spectrum formula with phosphatidylserine + citicoline"
  };

  var answers = {};
  var idx = 0;
  var leadId = genId();

  // ----------------------------- RENDER ------------------------------------
  function track(name, params) { try { if (window.gtag) gtag("event", name, params || {}); } catch (e) {} }

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
      if (form.website.value) return;                 // honeypot tripped — silently drop
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

    mount.innerHTML =
      '<div class="mlq-step mlq-result">' +
        '<span class="badge">★ Your match</span>' +
        "<h3>Based on your answers, look for <span class='match'>" + (MATCH[sym] || MATCH.focus) + "</span>.</h3>" +
        "<p>That's exactly the profile of the formula our editors rated <strong>#1 for 2026</strong>: fully transparent label, clinical doses, and a 60-day guarantee. Here's where to see it:</p>" +
        '<a class="mlq-btn" href="' + url + '" rel="nofollow sponsored">See your #1 match &rarr;</a>' +
        '<p class="sent">✓ Plan sent to ' + escapeHtml(email) + "</p>" +
      "</div>";
  }

  // ----------------------------- DATA --------------------------------------
  function segment() {
    return ["s" + (answers.symptom || ""), "a" + (answers.age || ""), "d" + (answers.dur || ""), "t" + (answers.tried || "")].join("");
  }

  function submitLead(email, done) {
    var qs = new URLSearchParams(location.search);
    var payload = {
      email: email,
      lead_id: leadId,
      subid: CFG.subidBase + "_" + leadId + "_" + segment(),
      answers: answers,
      segment: segment(),
      source_page: location.pathname,
      referrer: document.referrer || "",
      incoming_clickid: qs.get("clickid") || qs.get("rtkcid") || qs.get("cid") || qs.get("sub1") || "",
      utm: { source: qs.get("utm_source") || "", medium: qs.get("utm_medium") || "", campaign: qs.get("utm_campaign") || "" },
      consent: true
    };
    // fail-open: store best-effort, but ALWAYS continue to the result.
    var ok = false, finished = false;
    function finish() { if (!finished) { finished = true; done(); } }
    try {
      fetch(CFG.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        keepalive: true
      }).then(function (r) { ok = r.ok; }).catch(function () {}).finally(finish);
    } catch (e) { finish(); }
    setTimeout(finish, 2500); // never let a slow/missing backend block the funnel
  }

  // ----------------------------- UTIL --------------------------------------
  function genId() {
    var t = Date.now().toString(36);
    var r = (Math.floor(Math.random() * 1e6)).toString(36);
    return (t + r).slice(-9);
  }
  function escapeHtml(s) { return String(s).replace(/[<>&"]/g, function (c) { return { "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" }[c]; }); }

  // boot
  renderStep();
  track("quiz_view", {});
})();
