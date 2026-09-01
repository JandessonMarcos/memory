#!/usr/bin/env python3
"""
Render one article directory from a post spec, mirroring how-to-improve-memory/
exactly: same head boilerplate, same JSON-LD @graph, same header/topnav/footer,
same body furniture (.method, .sec, .recbox, .pull, .faq, .final, .sources).

The routine used to hand-copy the template for every post, which is where the
schema/markup drift between older posts came from. Specs live in
_automation/posts/<slug>.json; this renders them.

  python3 _automation/gen-post.py <slug> [<slug> ...]
"""
import sys, os, re, json

SITE = "https://www.memorylabdaily.com"
SPEC_DIR = "_automation/posts"

# category -> (breadcrumb label, breadcrumb href)
CATS = {
    "Memory":       ("Memory",       "/memory-basics/"),
    "Brain Health": ("Brain Health", "/brain-health-lifestyle/"),
    "Aging Well":   ("Aging Well",   "/brain-health-lifestyle/"),
    "Ingredients":  ("Ingredients",  "../citicoline-for-memory/"),
    "News":         ("News",         "/brain-health-lifestyle/"),
    "Reviews":      ("Reviews",      "../best-memory-supplements-2026/"),
}

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-KXS8VN6QK1"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-KXS8VN6QK1');</script>
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '831503250016369');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=831503250016369&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel Code -->

<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="index, follow">
<title>@@title_tag@@</title>
<meta name="description" content="@@desc@@">
<link rel="canonical" href="@@site@@/@@slug@@/">
<meta property="og:type" content="article">
<meta property="og:title" content="@@og_title@@">
<meta property="og:description" content="@@desc@@">
<meta property="og:url" content="@@site@@/@@slug@@/">
<meta property="og:site_name" content="Memory Lab">
<meta property="og:image" content="@@site@@/assets/img/@@slug@@.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/style.css">
<script type="application/ld+json">
@@ldjson@@
</script>
</head>
<body>
<!-- TOP ANNOUNCEMENT BAR -->
<div class="topbar"><div class="topbar-in"><span class="tb-dot"></span> <strong>Up to 40% of dementia risk comes from factors you can control.</strong> <a href="/how-to-improve-memory/">See the habits that protect your memory &rarr;</a></div></div>


<div class="ftc"><div class="ftc-inner"><strong>Advertising Disclosure:</strong> Memory Lab is reader-supported. We may earn a commission when you buy through links on our site, at no extra cost to you.</div></div>

<header class="header">
  <div class="header-inner">
    <button class="ico-grid" aria-label="Menu"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></button>
    <a class="logo" href="../index.html">Memory <span>Lab</span></a>
    <button class="ico-search" aria-label="Search"><svg viewBox="0 0 24 24" fill="none" stroke="#222" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg></button>
  </div>
</header>
<nav class="topnav">
  <div class="topnav-inner">
    <a href="../index.html">Home</a><a href="../best-memory-supplements-2026/">Reviews</a>
    <a href="../memory-basics/">Memory</a><a href="../foods-and-habits-for-memory/">Aging Well</a>
    <a href="../citicoline-for-memory/">Ingredients</a><a href="../about/">About</a>
  </div>
</nav>

<main>
  <article class="article">
    <div class="breadcrumb"><a href="../index.html">Home</a><span class="sep">&rsaquo;</span><a href="@@cat_href@@">@@cat_label@@</a><span class="sep">&rsaquo;</span><span class="current">@@crumb@@</span></div>

    <span class="cat">@@cat@@ &middot; Updated <span id="upd">2026</span></span>
    <h1 class="headline">@@h1_a@@<span class="hl">@@h1_b@@</span></h1>
    <p class="subhead">@@subhead@@</p>

    <div class="byline">
      <span class="av" aria-hidden="true">
        <svg viewBox="0 0 100 100"><rect width="100" height="100" fill="#e7f3f1"/><path d="M18 100 V83 C18 71 29 65 39 62 L50 71 L61 62 C71 65 82 71 82 83 V100 Z" fill="#fff"/><path d="M44 63 L50 79 L56 63 L52 59 H48 Z" fill="#1f9e8a"/><path d="M44 63 C40 82 58 84 60 71" fill="none" stroke="#5a6678" stroke-width="2.4"/><circle cx="60" cy="71" r="3.2" fill="#5a6678"/><rect x="44" y="52" width="12" height="13" rx="3" fill="#eab38f"/><circle cx="50" cy="41" r="16" fill="#f1c5a6"/><path d="M33 41 C31 31 38 24 50 24 C62 24 69 31 67 41 L62 39 C62 32 57 29 50 29 C43 29 38 32 38 39 Z" fill="#3a342f"/></svg>
      </span>
      <div>By <b>Sarah Coleman</b>, Health Editor &nbsp;&middot;&nbsp; Reviewed by <b>Dr. Marcus Reed, MD</b> &nbsp;&middot;&nbsp; <span id="pubdate">Published @@pubdate_h@@</span></div>
    </div>

    <img width="900" height="600" class="article-hero" src="../assets/img/@@slug@@.jpg" alt="@@alt@@" loading="lazy">

    <div class="method">
      <h3>Key takeaways</h3>
      <ul>
@@takeaways@@
      </ul>
    </div>

@@body@@

    <div class="pull">@@pull@@</div>

    <h2 class="sec">Frequently asked questions</h2>
    <div class="faq">
@@faq_html@@
    </div>

    <!-- final CTA -->
    <div class="final">
      <h3>@@final_h@@</h3>
      <p>@@final_p@@</p>
      <a class="buy-btn buy-link" data-rank="1" href="#">See the Top 5 Memory Formulas &rarr;</a>
    </div>

    <div class="sources" style="font-size:14px;margin-top:22px;padding-top:14px;border-top:1px solid #e6e8ec">
      <strong>Sources &amp; further reading</strong>
      <ul style="margin:8px 0 0;padding-left:18px;line-height:1.7">@@sources@@</ul>
    </div>
    <p style="font-size:14px;margin-top:18px"><strong>Related:</strong> @@related@@</p>
  </article>
</main>

<div class="disclaimer">
  <strong>Disclaimer:</strong> This article is for educational purposes only and is not intended to diagnose, treat, cure, or prevent any disease. Individual results may vary. Statements have not been evaluated by the FDA. We may receive compensation when you purchase through links on this page. Always consult your physician before starting any new supplement.
</div>

<footer>
  <div class="footer-inner">
    <div>&copy; <span id="yr"></span> Memory <span class="fbrand">Lab</span>. All rights reserved.</div>
    <div class="footer-links"><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms of Use</a><a href="/advertising-disclosure/">Advertising Disclosure</a><a href="../about/">About</a></div>
  </div>
</footer>

<script src="../assets/cta.js"></script>
</body>
</html>
'''

RECBOX = '''    <!-- inline recommendation -->
    <div class="recbox">
      <div><div class="bottle xs"><div class="cap"></div><div class="body"><div class="label"><b>MEMORY<br>COMPLEX</b><div class="ln"></div><div class="ln"></div></div></div></div></div>
      <div>
        <span class="rb-badge">&#9733; Editors' #1 pick</span>
        <h4>The memory formula we rate highest in 2026</h4>
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733; <span style="color:#666;font-weight:700;font-size:12px">9.6/10</span></div>
        <p>One formula combined a fully transparent, clinically-dosed label &mdash; citicoline, bacopa, phosphatidylserine and B-vitamins &mdash; with a 60-day guarantee.</p>
        <a class="buy-btn sm buy-link" data-rank="1" href="#">See Today's Price &rarr;</a>
        <div style="margin-top:8px;font-size:13px"><a href="../best-memory-supplements-2026/">Read our full Top 5 review &rarr;</a></div>
      </div>
    </div>
'''


# Variant for branded review/comparison pages. The generic RECBOX above names a
# different ingredient list ("citicoline, bacopa, phosphatidylserine and
# B-vitamins"), which contradicts the article on any page that prints the real
# 5-ingredient panel. Branded pages use this one instead.
RECBOX_BRAND = '''    <!-- inline recommendation (branded page) -->
    <div class="recbox">
      <div><div class="bottle xs"><div class="cap"></div><div class="body"><div class="label"><b>MEMORY<br>COMPLEX</b><div class="ln"></div><div class="ln"></div></div></div></div></div>
      <div>
        <span class="rb-badge">&#9733; Editors' #1 pick</span>
        <h4>The memory formula we rate highest in 2026</h4>
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733; <span style="color:#666;font-weight:700;font-size:12px">9.6/10</span></div>
        <p>Five studied botanicals and amino acids in one label, bacopa and rhodiola among them, backed by a 60-day money-back guarantee.</p>
        <a class="buy-btn sm buy-link" data-rank="1" href="#">See Today's Price &rarr;</a>
        <div style="margin-top:8px;font-size:13px"><a href="../best-memory-supplements-2026/">Read our full Top 5 review &rarr;</a></div>
      </div>
    </div>
'''

def build_ldjson(s, slug, cat_label, cat_href):
    url = f"{SITE}/{slug}/"
    crumb_item = cat_href if cat_href.startswith("/") else "/" + cat_href.strip("./")
    graph = [
        {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Memory Lab", "url": f"{SITE}/",
         "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/og-default.png"}},
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Memory Lab",
         "publisher": {"@id": f"{SITE}/#org"}},
        {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": cat_label, "item": SITE + crumb_item},
            {"@type": "ListItem", "position": 3, "name": s["crumb"], "item": url}]},
        {"@type": "Article", "@id": f"{url}#article", "headline": s["og_title"],
         "description": s["desc"], "datePublished": s["date"], "dateModified": s["date"],
         "inLanguage": "en-US", "mainEntityOfPage": url,
         "image": f"{SITE}/assets/img/{slug}.jpg",
         "author": {"@id": f"{SITE}/about/#sarah-coleman"},
         "reviewedBy": {"@id": f"{SITE}/about/#marcus-reed"},
         "publisher": {"@id": f"{SITE}/#org"}},
        {"@type": "Person", "@id": f"{SITE}/about/#sarah-coleman", "name": "Sarah Coleman",
         "jobTitle": "Health Editor", "url": f"{SITE}/about/"},
        {"@type": "Person", "@id": f"{SITE}/about/#marcus-reed", "name": "Dr. Marcus Reed, MD",
         "jobTitle": "Medical Reviewer", "url": f"{SITE}/about/"},
        {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in s["faq"]]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      indent=2, ensure_ascii=False)


def render(slug):
    s = json.load(open(f"{SPEC_DIR}/{slug}.json"))
    cat_label, cat_href = CATS[s["cat"]]

    # body: list of ["h2", text] / ["p", html] / ["recbox"]
    parts = []
    for node in s["body"]:
        if node[0] == "h2":
            parts.append(f'    <h2 class="sec">{node[1]}</h2>')
        elif node[0] == "p":
            parts.append(f'    <p>{node[1]}</p>')
        elif node[0] == "recbox":
            variant = node[1] if len(node) > 1 else None
            box = RECBOX_BRAND if variant == "brand" else RECBOX
            parts.append(box.rstrip("\n"))
        elif node[0] == "h3":
            parts.append(f'    <h3>{node[1]}</h3>')
        elif node[0] == "ul":
            lis = "\n".join(f"      <li>{x}</li>" for x in node[1])
            parts.append(f'    <ul>\n{lis}\n    </ul>')
        elif node[0] == "table":
            # ["table", [headers...], [[cells...], ...]]
            head = "".join(f"<th>{h}</th>" for h in node[1])
            rows = "\n".join(
                "        <tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                for r in node[2])
            parts.append(
                '    <div class="cmp-wrap">\n'
                '      <table class="cmp">\n'
                f'        <thead><tr>{head}</tr></thead>\n'
                f'        <tbody>\n{rows}\n        </tbody>\n'
                '      </table>\n'
                '    </div>')
        else:
            raise SystemExit(f"{slug}: unknown body node {node[0]}")
    body = "\n\n".join(parts)

    takeaways = "\n".join(f"        <li>{t}</li>" for t in s["takeaways"])
    faq_html = "\n".join(
        f'      <details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>'
        for i, (q, a) in enumerate(s["faq"]))
    sources = "".join(
        f'<li><a href="{u}" rel="noopener" target="_blank">{t}</a></li>' for t, u in s["sources"])
    related = " &middot; ".join(f'<a href="../{u}/">{t}</a>' for t, u in s["related"])

    y, m, d = s["date"].split("-")
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    pubdate_h = f"{months[int(m)-1]} {int(d)}, {y}"

    # Token substitution rather than str.format: the head carries inline gtag and
    # fbq JavaScript full of literal braces, which .format() tries to parse.
    fields = {
        "title_tag": s["title_tag"], "desc": s["desc"], "og_title": s["og_title"],
        "site": SITE, "slug": slug,
        "ldjson": build_ldjson(s, slug, cat_label, cat_href),
        "cat": s["cat"], "cat_href": cat_href, "cat_label": cat_label, "crumb": s["crumb"],
        "h1_a": s["h1_a"], "h1_b": s["h1_b"], "subhead": s["subhead"],
        "pubdate_h": pubdate_h, "alt": s["alt"], "takeaways": takeaways, "body": body,
        "pull": s["pull"], "faq_html": faq_html, "final_h": s["final_h"],
        "final_p": s["final_p"], "sources": sources, "related": related,
    }
    out = HEAD
    for k, v in fields.items():
        out = out.replace("@@" + k + "@@", str(v))
    leftover = re.findall(r"@@(\w+)@@", out)
    if leftover:
        raise SystemExit(f"{slug}: unresolved tokens {set(leftover)}")

    os.makedirs(slug, exist_ok=True)
    with open(f"{slug}/index.html", "w") as f:
        f.write(out)

    def _text(n):
        if n[0] in ("h2", "h3", "p"):
            return n[1]
        if n[0] == "ul":
            return " ".join(n[1])
        if n[0] == "table":
            return " ".join(n[1]) + " " + " ".join(c for r in n[2] for c in r)
        return ""
    words = len(re.sub(r"<[^>]+>", " ", " ".join(_text(n) for n in s["body"])).split())
    em = out.count("—")
    print(f"OK {slug}  words~{words}  em-dashes={em}  faq={len(s['faq'])}")
    if em > 1:
        print(f"   WARN {slug}: {em} em dashes (cap is 1)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for slug in sys.argv[1:]:
        render(slug)
