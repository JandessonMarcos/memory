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
    "Sleep":               ("Sleep",               "/topics/sleep/"),
    "Heart Health":        ("Heart Health",        "/topics/heart/"),
    "Gut Health":          ("Gut Health",          "/topics/gut/"),
    "Energy & Metabolism": ("Energy & Metabolism", "/topics/energy/"),
    "Joints & Mobility":   ("Joints & Mobility",   "/topics/joints/"),
    "Men's Health":        ("Men's Health",        "/topics/men/"),
    "Women's Health":      ("Women's Health",      "/topics/women/"),
    "Nutrition":           ("Nutrition",           "/topics/nutrition/"),
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
      <div>By the <b>Memory Lab editorial team</b> &nbsp;&middot;&nbsp; <a href="../editorial-policy/">How we research and write</a> &nbsp;&middot;&nbsp; <span id="pubdate">Published @@pubdate_h@@</span></div>
    </div>

    <img width="900" height="600" class="article-hero" src="../assets/img/@@slug@@.jpg" alt="@@alt@@" loading="lazy">
@@img_credit@@

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
      <a class="buy-btn @@buy_cls@@" data-rank="1" href="#">@@final_btn@@</a>
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
@@brand_js@@</body>
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

# Branded pages (spec "brand"). MemoHoney buttons use a.buy-link-mhny, wired by
# assets/cta-mhny.js to /go/memohoney/; Memopezil keeps a.buy-link (cta.js).
# Prices mirror the review pages; change them in both places together.
BRANDS = {
    "memopezil": {"name": "Memopezil", "cls": "buy-link", "packs": "packs", "js": "",
                  "line": "Five ingredients with every dose printed: BCAAs, bacopa, rhodiola, L-theanine and panax ginseng. Two capsules a day, stimulant-free.",
                  "ship2": "+ shipping"},
    "memohoney": {"name": "MemoHoney", "cls": "buy-link-mhny", "packs": "packs-mhny",
                  "js": '<script src="../assets/cta-mhny.js"></script>\n',
                  "line": "A blood-flow-first formula with ginkgo, bacopa, blueberry and honey. One capsule a day, stimulant-free.",
                  "ship2": "+ $9.99 shipping"},
}

# Every other affiliate offer comes from _automation/offers.json (build-offers.py
# builds its /go/ page and cta-<key>.js). Spec "brand" = the offer's slug.
for _o in json.load(open("_automation/offers.json"))["offers"]:
    BRANDS[_o["slug"]] = {"name": _o["name"], "cls": "buy-link-" + _o["key"], "packs": "packs-" + _o["key"],
                          "js": f'<script src="../assets/cta-{_o["key"]}.js"></script>\n',
                          "line": _o["line"], "ship2": _o["ship2"]}

PRODBOX = '''    <div class="prodbox">
      <img src="../assets/img/@@packs@@/6.png" width="520" height="520" alt="@@name@@ bottles from the official store" loading="lazy">
      <div>
        <span class="pb-tag">Official store</span>
        <h4>@@name@@: check today's price</h4>
        <p>@@line@@ Sold only on the official site, with a 60-day money-back guarantee.</p>
        <a class="buy-btn sm @@cls@@" data-rank="@@rank@@" href="#">See the official price &rarr;</a>
      </div>
    </div>
'''

PACKBOX = '''    <div class="packbox">
      <a class="pack-opt @@cls@@" data-pack="2" data-rank="@@rank@@">
        <img class="po-img" src="../assets/img/@@packs@@/2.png" width="520" height="520" alt="@@name@@ 2-bottle package" loading="lazy">
        <span class="po-top">2 Bottles · Starter</span>
        <span class="po-price">$79<small>/bottle</small></span>
        <span class="po-cta">Check Availability &rarr;</span>
        <span class="po-ship">@@ship2@@</span>
      </a>
      <a class="pack-opt best @@cls@@" data-pack="6" data-rank="@@rank@@">
        <img class="po-img" src="../assets/img/@@packs@@/6.png" width="520" height="520" alt="@@name@@ 6-bottle package, best value" loading="lazy">
        <span class="po-top">6 Bottles · Best Value</span>
        <span class="po-price">$49<small>/bottle</small></span>
        <span class="po-cta">Claim Discount &rarr;</span>
        <span class="po-ship">Free US Shipping</span>
      </a>
      <a class="pack-opt @@cls@@" data-pack="3" data-rank="@@rank@@">
        <img class="po-img" src="../assets/img/@@packs@@/3.png" width="520" height="520" alt="@@name@@ 3-bottle package" loading="lazy">
        <span class="po-top">3 Bottles · Popular</span>
        <span class="po-price">$69<small>/bottle</small></span>
        <span class="po-cta">Claim Discount &rarr;</span>
        <span class="po-ship">Free US Shipping</span>
      </a>
    </div>
    <div class="grt-line"><span class="tk">&#10003;</span> 60-Day Money-Back Guarantee · Official site only · One-time charge</div>
    <p class="pricenote">Prices shown are the manufacturer's published rates at the time of writing and can change without notice.</p>
'''


def brand_block(tpl, brand, rank):
    b = BRANDS[brand]
    out = tpl
    for k, v in (("name", b["name"]), ("cls", b["cls"]), ("packs", b["packs"]),
                 ("line", b["line"]), ("ship2", b["ship2"]), ("rank", str(rank))):
        out = out.replace("@@" + k + "@@", v)
    return out.rstrip("\n")


def figure(file, alt, caption):
    """Inline photo. Credit goes in the caption when the licence asks for it."""
    key = os.path.splitext(os.path.basename(file))[0]
    cred = ""
    try:
        c = json.load(open(CREDITS_FILE)).get(key)
    except Exception:
        c = None
    if c and c.get("license") not in ("CC0", "Public domain", None):
        who = c.get("creator") or "Unknown"
        src = c.get("source") or ""
        who_h = f'<a href="{src}" rel="noopener nofollow" target="_blank">{who}</a>' if src else who
        cred = f' <span class="fig-credit">Photo: {who_h} / {c.get("license")}</span>'
    try:
        from PIL import Image
        w, h = Image.open(f"assets/img/{file}").size
    except Exception:
        w, h = 900, 600
    return (f'    <figure class="inl">\n'
            f'      <img src="../assets/img/{file}" width="{w}" height="{h}" alt="{alt}" loading="lazy">\n'
            f'      <figcaption>{caption}{cred}</figcaption>\n'
            f'    </figure>')


CREDITS_FILE = "_automation/img-credits.json"
POOL_MANIFEST = "_automation/img-pool.json"


def hero_credit(slug):
    """Credit line for the hero. CC BY and CC BY-SA require it.

    Looks in img-credits.json (Openverse path) then the pool manifest, which has
    carried license + attribution all along. Returns "" when the image is CC0 or
    public domain, where no credit is owed.
    """
    try:
        c = json.load(open(CREDITS_FILE)).get(slug)
    except Exception:
        c = None
    if c:
        lic = c.get("license", "")
        if lic in ("CC0", "Public domain"):
            return ""
        who = c.get("creator") or "Unknown"
        src = c.get("source") or ""
        lurl = c.get("license_url") or ""
        who_h = f'<a href="{src}" rel="noopener nofollow" target="_blank">{who}</a>' if src else who
        lic_h = f'<a href="{lurl}" rel="license noopener nofollow" target="_blank">{lic}</a>' if lurl else lic
        return f'    <p class="img-credit">Photo: {who_h} / {lic_h}</p>'

    try:
        d = json.load(open(POOL_MANIFEST))
        items = d if isinstance(d, list) else (d.get("images") or d.get("items") or [])
        e = next((i for i in items if i.get("used_by") == slug), None)
    except Exception:
        e = None
    if not e:
        return ""
    lic = e.get("license", "")
    if lic in ("CC0", "Public domain"):
        return ""
    who = e.get("attribution") or "Unknown"
    src = e.get("descurl") or ""
    who_h = f'<a href="{src}" rel="noopener nofollow" target="_blank">{who}</a>' if src else who
    return f'    <p class="img-credit">Photo: {who_h} / {lic}</p>'


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
         "author": {"@id": f"{SITE}/#org"},
         "publisher": {"@id": f"{SITE}/#org"}},

        {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in s["faq"]]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      indent=2, ensure_ascii=False)


def _live(target, slug):
    return target == slug or os.path.isdir(target)


def unlink_missing(html, slug):
    """Prewritten pages link siblings that publish on later days. Until a sibling
    exists, show its anchor as plain text instead of a 404; re-rendering after
    each publish (--refresh-prewritten) turns the link back on."""
    return re.sub(r'<a href=[\'"]\.\./([a-z0-9-]+)/[\'"][^>]*>(.*?)</a>',
                  lambda m: m.group(0) if _live(m.group(1), slug) else m.group(2), html)


def render(slug):
    s = json.load(open(f"{SPEC_DIR}/{slug}.json"))
    s["body"] = [[n[0], unlink_missing(n[1], slug)] + n[2:] if n[0] in ("p", "h2", "h3") else
                 ([n[0], [unlink_missing(x, slug) for x in n[1]]] if n[0] == "ul" else n)
                 for n in s["body"]]
    s["faq"] = [[q, unlink_missing(a, slug)] for q, a in s["faq"]]
    s["related"] = [r for r in s["related"] if _live(r[1], slug)]
    cat_label, cat_href = CATS[s["cat"]]

    # body: list of ["h2", text] / ["p", html] / ["recbox"]
    brand = s.get("brand")
    parts = []
    rank = 0
    for node in s["body"]:
        if node[0] == "h2":
            parts.append(f'    <h2 class="sec">{node[1]}</h2>')
        elif node[0] == "p":
            parts.append(f'    <p>{node[1]}</p>')
        elif node[0] == "recbox":
            variant = node[1] if len(node) > 1 else None
            box = RECBOX_BRAND if variant == "brand" else RECBOX
            parts.append(box.rstrip("\n"))
        elif node[0] in ("prodbox", "packs"):
            if not brand:
                raise SystemExit(f"{slug}: {node[0]} needs a spec 'brand'")
            rank += 1
            parts.append(brand_block(PRODBOX if node[0] == "prodbox" else PACKBOX, brand, rank))
        elif node[0] == "figure":
            parts.append(figure(node[1], node[2], node[3]))
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
        "img_credit": hero_credit(slug),
        "pull": s["pull"], "faq_html": faq_html, "final_h": s["final_h"],
        "final_p": s["final_p"], "sources": sources, "related": related,
        "buy_cls": BRANDS[brand]["cls"] if brand else "buy-link",
        "final_btn": (f'See {BRANDS[brand]["name"]}\'s official price &rarr;' if brand
                      else "See the Top 5 Memory Formulas &rarr;"),
        "brand_js": BRANDS[brand]["js"] if brand else "",
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
    args = sys.argv[1:]
    if "--refresh-prewritten" in args:
        # re-render every prewritten page already live, so links to siblings
        # published since then switch on
        args.remove("--refresh-prewritten")
        q = json.load(open("_automation/content-queue.json"))["queue"]
        args += [i["slug"] for i in q if i.get("prewritten") and i.get("status") == "done"
                 and os.path.isdir(i["slug"]) and i["slug"] not in args]
    for slug in args:
        render(slug)
