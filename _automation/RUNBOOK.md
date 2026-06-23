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
3. **Image — curate with your own eyes (critical for quality):**
   - Query Openverse for **concrete subjects** (people, objects, real scenes — e.g., "senior couple walking", "salmon fillet", "microscope lab"), NOT abstract concepts. Prefer `source=stocksnap&license=cc0`; fall back to `license=cc0` without source.
   - Download **3-4 candidates** to /tmp, then **OPEN EACH with the Read tool and LOOK at it.** Pick the best **real photograph** that matches the topic.
   - **REJECT:** diagrams, charts, brain scans/MRIs, illustrations, clip-art, gradients/abstract renders, anything with watermarks/text, and any file **< 40 KB** (usually junk/flat).
   - Resize the chosen one with **Python Pillow** (cloud = **Linux, do NOT use `sips`**; `pip install --quiet Pillow` if missing): `python3 -c "from PIL import Image; im=Image.open('in.jpg').convert('RGB'); im.thumbnail((1100,1100)); im.save('assets/img/<slug>.jpg', quality=85)"`.
   - If no good photo is found after a few queries, **reuse a relevant existing image from assets/img/** rather than shipping an ugly one.
4. Add a card to the right home section + add the URL to `sitemap.xml`.
5. **Quality gate** (skip & log if fails): word count ≥ 900, has Article+FAQPage schema, single H1, links to pillar + money page, no "Memopezil", slug not duplicated.
6. Mark each done in the queue: `"status":"done","published":"<date>"`.
7. **Commit and push to `main`** with a clear message (e.g., `content: <slugs> + news`). Publishing is automatic: Cloudflare Pages is connected to this repo (Git integration) and deploys every push. *(If ever running locally instead, deploy with `CLOUDFLARE_ACCOUNT_ID=b3b59e6ff582d44cfddea9c40ffafde1 npx -y wrangler@latest pages deploy <blogdir> --project-name memorylabdaily --branch main`.)*
8. Log what was published (and what was skipped) at the end of the run.

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
- **Deploy auth**: needs Cloudflare creds. Local = uses `~/.wrangler` OAuth. Cloud = needs a `CLOUDFLARE_API_TOKEN` secret (Pages:Edit) configured on the routine.
