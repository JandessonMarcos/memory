# Memory Lab — Daily content routine (RUNBOOK)

**Goal:** publish a *small, safe* batch of genuinely useful SEO+GEO articles per day on a NEW domain, without manual triggering. Quality > quantity (avoid Google's scaled-content-abuse penalty).

## Cadence (ramp — do NOT exceed)
- Week 1: **2 articles/day**
- Week 2+: **3 articles/day**
- Never publish more than 3/day while the domain is < ~6 months old.

## Each daily run does:
1. Read `_automation/content-queue.json`. Pick the top **N** items with `status: "pending"` (N per ramp). Skip any slug already in `published_base` or `status: "done"`.
2. For EACH picked topic, generate `/<slug>/index.html` by mirroring the template **`how-to-improve-memory/index.html`** exactly:
   - `<meta charset>` + favicon line, FTC bar, header, topnav, footer, disclaimer, byline SVG.
   - Full JSON-LD @graph: Organization, WebSite, BreadcrumbList, Article (author #sarah-coleman, reviewedBy #marcus-reed, publisher #org, dates = today, en-US), 2 Person nodes, FAQPage matching the visible FAQ EXACTLY.
   - GEO: `.method` Key takeaways, direct-answer intro, question-style `h2.sec`, `.pull` quote, `.faq` `<details>`.
   - One `.recbox` mid + one `.final` banner, both `<a class="buy-btn ... buy-link" data-rank="1" href="#">`.
   - Internal links: MUST link the pillar `../how-to-improve-memory/`, the money page `../best-memory-supplements-2026/`, and 1–2 topically-related spokes.
   - canonical/og/url = `https://www.memorylabdaily.com/<slug>/`. og:image = `/assets/img/<slug>.jpg`.
   - ~1000–1500 words. Accurate, hedged, NO fabricated studies/stats. English/US. Brand "Memory Lab". NEVER write "Memopezil"; editorial #1 = "Advanced Memory Complex".
   - **Write like a human (see `## Writing style` below).** Mirror the template's *structure and markup*, NOT its punctuation habits: the old posts overuse the em dash, so do not copy that density.
3. **Image — sourcing is DETERMINISTIC, do NOT freelance it:**
   - **⛔ NEVER generate, draw, or synthesize a hero image.** Do not use PIL/ImageDraw/numpy/any tool to make gradients, grain/noise textures, abstract bubble/circle renders, solid colors, or "natural texture" fills. Every past image disaster (green/gold/blue rectangles, grain fills, bubble art) came from the routine *inventing* an image when sourcing felt hard. Sourcing is never optional; a synthetic fill is always worse than trying another query.
   - **Run the sourcing script per slug** — it queries Openverse, validates (structure + colors + uniqueness), and installs a real photo resized to 900px, all in one shot:
     ```
     python3 _automation/source-image.py <slug> "concrete subject" "alt subject" "another angle"
     ```
     Pass **concrete subjects** (people, objects, real scenes — e.g. "senior couple walking", "salmon fillet plate", "microscope lab bench"), NOT abstract concepts. Give 3-4 different subject phrases so it has fallbacks.
   - If it prints **`OK`**, the image is installed and already passes the real-photo + uniqueness gates. If it prints **`MISS`**, re-run with *different, more concrete* subject phrases (a different scene/person/object/setting for the same topic). Keep going until it prints OK. Never fall back to generating or reusing an image.
   - **After it installs, still OPEN the file with the Read tool and LOOK.** The gate guarantees "a real, unique photo," not "the right subject." If it's off-topic (e.g. a religious painting for "study tips"), re-run the script with sharper subject phrases.
   - **NEVER reuse an existing image as a fallback**, and never let one source photo serve two slugs — the script's uniqueness guard enforces this, do not work around it.
4. **Home placement — newest first:** insert the new post's card at the **TOP** of the **`Latest`** section in `index.html` (as the first child of that section's `.card-grid`, right after `<p class="section-label">Latest</p>`). Keep **Latest capped at 4 cards**: if it now exceeds 4, move the **oldest** (last) card out of Latest and append it to its proper **thematic** section (`Memory & brain health`, `Ingredients & evidence`, `Reviews & comparisons`, or `Bill Gates & brain research`) based on its category/topic. Then add the URL to `sitemap.xml`. *(Copy an existing `.post-card` block verbatim for the markup; NEVER let the same slug appear in two sections.)*
4b. **Rotate the home lead story every 2 days (freshness):** The Portal Hero lead in `index.html` (`<a class="ph-lead" …>`) must not go stale. On each run, check which slug it points to. If the **same** lead has been featured for **≥ 2 days**, swap the entire `.ph-lead` block (href + `.ph-img` `<img>` with correct `width`/`height` + `.ph-cat` + `<h2>` + `<p>`) to a different high-interest post — a recent news item or a strong evergreen with a good real photo. Move the outgoing lead into the `Top stories` sidebar if it isn't already prominent elsewhere. Never feature a post whose image is a flat gradient (see the image gate below).
5. **Quality gate** (skip & log if fails): word count ≥ 900, has Article+FAQPage schema, single H1, links to pillar + money page, no "Memopezil", slug not duplicated, **≤ 1 em dash (—) in the whole article**. **Image gate — run BOTH audits at the end of the run; both MUST print `OK` before you commit:**
   - `python3 _automation/check-image-real.py --audit` → rejects synthetic junk (gradients, grain/noise textures, abstract renders, clip-art, monochrome fills). This gate measures *structure on a downscaled copy* + distinct-color count. **Do NOT use the old full-res edge-energy one-liner** — grain and checkerboards pass it (noise = high local diff), which is exactly how the "natural grain texture" heroes shipped. If this prints `FAIL`, re-source that slug with `source-image.py` (never hand-fix the pixels).
   - `python3 _automation/check-image-unique.py --audit` → must print `OK` (zero colliding groups).
6. Mark each done in the queue: `"status":"done","published":"<date>"`.
7. **Commit and push to `main`** with a clear message (e.g., `content: <slugs> + news`). Publishing is automatic: this project is a **Cloudflare Worker with Static Assets** (`wrangler.jsonc` → name `memory`, `main: src/index.js`, `assets.directory: "."`, D1 binding `DB`), connected to this repo via Git integration, which deploys every push to `main`. The Worker serves every static file and adds the `POST /api/lead` route (`src/index.js`). *(If ever deploying manually instead, run from the blog dir: `CLOUDFLARE_ACCOUNT_ID=b3b59e6ff582d44cfddea9c40ffafde1 npx -y wrangler@latest deploy`. Do NOT use `wrangler pages deploy` — this is a Worker, not a Pages project.)* Note: `functions/api/lead.js` is a legacy Pages-Function mirror of the same lead handler and is **not** used by the Worker; leave it or remove it, but the live `/api/lead` route lives in `src/index.js`.
8. Log what was published (and what was skipped) at the end of the run.

## Writing style: sound human (anti-AI-tell)
Affiliate + YMYL content has to read like a person wrote it. That is an E-E-A-T, anti-spam-review, and conversion requirement, not a nicety. Bake these into every generation:

- **Em dash (—): 1 per article, maximum.** It is the #1 "written by AI" tell, and the model defaults to overusing it. Replace it with a period (splitting into two sentences is best, because it varies the rhythm), a comma, a colon, or parentheses. *(The en dash "–" in number ranges like "1–3 weeks" is correct typography. Keep those.)*
- **Vary sentence length (burstiness).** Mix long sentences with short ones. Let some land under 8 words. A run of uniform, medium-length sentences is the clearest machine signature.
- **Cut the tell-tale constructions:** "it's not just X, it's Y", "here's the thing", "the truth is", "let's be honest", a rule-of-three in every list, and wrap-ups like "in conclusion / ultimately / at the end of the day".
- **Cut the tell-tale words:** delve, robust, boost, leverage, navigate, testament, crucial, vital, unlock, elevate, realm, foster, myriad, seamless, game-changer. Use plain ones instead.
- **Do not open consecutive sentences or paragraphs the same way.** Vary how each one starts.
- **Use contractions, an occasional fragment, and concrete nouns.** Write the way the byline persona (a health editor) actually speaks.

Self-check before saving each article: count the em dashes (must be ≤ 1), scan the first word of every paragraph (are they varied?), and confirm two or three sentences run under 8 words.

## When the queue runs low
When < 6 `pending` remain, generate ~20 new long-tail, low-KD memory/brain topics (distinct from everything published) and append them as `pending`.

## News / freshness track (newsjacking) — "publish on each new study"
Besides the evergreen queue, scan reputable sources for NEW brain/memory/Alzheimer's research and publish a timely post per genuinely new item (Google rewards freshness; AI Overviews favor recent, sourced content).
- **Priority watch — WebFetch these directly each run** (high-authority; cite + link them for E-E-A-T):
  - Harvard Health — Memory hub: https://www.health.harvard.edu/topics/memory  (lists recent memory articles → great for fresh, citable angles)
  - NINDS / NIH — Brain Basics: https://www.ninds.nih.gov/health-information/public-education/brain-basics/brain-basics-know-your-brain  (authoritative reference to cite)
- **Also scan (last ~7 days)** via WebSearch + WebFetch:
  - Universities/medical: NIH / NIA, Harvard Health, Mayo Clinic, Cleveland Clinic, Stanford & MIT news, Alzheimer's Association (alz.org).
  - Health/science portals: ScienceDaily, Medical News Today, Healthline, WebMD, EurekAlert.
  - **Always link to the original source** (never copy text); add original "what this means for you" analysis.
- For each NEW, relevant item not already in `_automation/news-covered.json`:
  1. Write a **news-style** article: summarize the finding in plain English, add an original **"What this means for you"** analysis, **cite + link the original source**, end with a soft funnel to the pillar/offer. `cat: "News"`. datePublished = dateModified = today.
  2. Schema: Article (NewsArticle ok), with `dateModified`. Keep FAQ optional.
  3. **Accuracy is paramount (YMYL):** only real, sourced facts; NO fabricated studies, quotes or stats; hedge; doctor caveat.
  4. Append the source URL to `_automation/news-covered.json` (dedup).
- **Cap:** at most 1–2 news posts/day, and never exceed the **total daily cap of 3** while the domain is new.

## Requirements to run unattended
- **Files**: this routine needs access to the blog folder. (Local cron = uses these files directly. Cloud routine = needs the project in a Git repo it can clone.)
- **Deploy auth**: needs Cloudflare creds. Local = uses `~/.wrangler` OAuth. Cloud = needs a `CLOUDFLARE_API_TOKEN` secret with **Workers Scripts:Edit** (and, since this Worker binds D1, **D1:Edit**) configured on the routine. *(Not "Pages:Edit" — this deploys a Worker.)*
