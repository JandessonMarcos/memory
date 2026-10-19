#!/usr/bin/env python3
"""
Site chrome + home builder (portal layout, added 2026-10-19).

Run after publishing, before the gates:
  python3 _automation/site.py

What it does, every run, deterministically:
  1. Reads every <slug>/index.html that carries an Article (datePublished) and
     builds the post list: title, description, date, category, hero image.
  2. Rewrites the shared header/nav on EVERY page (one source of truth: HEADER
     below), moves the FTC disclosure under it, adds the article sidebar slot
     and the /assets/chrome.js script.
  3. Regenerates the home (index.html) and one hub page per section under
     /topics/<slug>/, plus assets/latest.json for the article sidebar, and adds
     the hub URLs to sitemap.xml.

The home is no longer edited by hand: newest post = lead story, sections fill
themselves by category. To add a section, add it to CATS and map the queue's
`cat` value in CAT_MAP.
"""
import glob, html, json, os, re

try:
    from PIL import Image
except Exception:
    Image = None

SITE = "https://www.memorylabdaily.com"

# (slug, label, one-line description). Order = nav order = home section order.
CATS = [
    ("memory-brain", "Memory & Brain", "Memory, focus, brain fog and how the brain ages."),
    ("sleep", "Sleep", "Sleep quality, insomnia, naps and what rest does for the body and mind."),
    ("heart", "Heart Health", "Blood pressure, cholesterol, circulation and everyday heart habits."),
    ("gut", "Gut Health", "Digestion, the microbiome, bloating and the gut-brain connection."),
    ("energy", "Energy & Metabolism", "Fatigue, blood sugar, weight and metabolic health."),
    ("joints", "Joints & Mobility", "Joint pain, flexibility, bone health and staying mobile."),
    ("men", "Men's Health", "Testosterone, prostate, fitness and health after 40 for men."),
    ("women", "Women's Health", "Hormones, menopause, bone health and wellbeing for women."),
    ("nutrition", "Nutrition", "Foods, diets and eating patterns, explained without the hype."),
    ("healthy-aging", "Healthy Aging", "Habits that keep body and mind working well with age."),
    ("supplements", "Supplements", "Ingredients and supplements: what the evidence supports."),
    ("reviews", "Reviews", "Independent product reviews and comparisons."),
    ("news", "News", "New research, explained in plain English."),
]
CAT_LABEL = {s: l for s, l, _ in CATS}

# queue / search-index `cat` value -> section slug
CAT_MAP = {
    "memory": "memory-brain", "brain health": "memory-brain", "brain health · updated": "memory-brain",
    "memory & brain": "memory-brain", "brain": "memory-brain", "focus": "memory-brain",
    "sleep": "sleep",
    "heart health": "heart", "heart": "heart",
    "gut health": "gut", "gut": "gut", "digestion": "gut",
    "energy & metabolism": "energy", "energy": "energy", "metabolism": "energy",
    "joints & mobility": "joints", "joints": "joints", "mobility": "joints",
    "men's health": "men", "mens health": "men",
    "women's health": "women", "womens health": "women",
    "nutrition": "nutrition",
    "aging well": "healthy-aging", "healthy aging": "healthy-aging",
    "ingredients": "supplements", "supplements": "supplements",
    "reviews": "reviews", "independent review": "reviews",
    "news": "news",
}

# fixed evergreen picks for the "Editors' picks" row (skipped if missing)
PICKS = ["how-to-improve-memory", "best-memory-supplements-2026", "brain-fog-causes-and-fixes", "sleep-and-memory"]

# money pages keep the reader on the offer: no "Latest" sidebar
NO_ASIDE = {"best-memory-supplements-2026"}

SKIP_DIRS = {"assets", "_automation", "src", "functions", "go", "topics", "node_modules"}


def esc(s):
    return html.escape(s or "", quote=True)


def cat_slug(name):
    return CAT_MAP.get((name or "").strip().lower())


# ---------------------------------------------------------------- posts
def load_posts():
    idx = {}
    try:
        for it in json.load(open("assets/search-index.json")):
            idx[it.get("u", "").strip("/")] = it.get("c", "")
    except Exception:
        pass
    posts = []
    for p in glob.glob("*/index.html"):
        slug = p.split("/")[0]
        if slug in SKIP_DIRS:
            continue
        s = open(p, encoding="utf-8").read()
        m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', s)
        if not m or '<article class="article">' not in s:
            continue
        date = m.group(1)
        t = re.search(r'<meta property="og:title" content="([^"]*)"', s) or re.search(r"<title>(.*?)</title>", s, re.S)
        title = html.unescape(t.group(1)).strip() if t else slug
        title = re.sub(r"\s*[|—-]\s*Memory Lab\s*$", "", title)
        d = re.search(r'<meta name="description" content="([^"]*)"', s)
        desc = html.unescape(d.group(1)) if d else ""
        cat = cat_slug(idx.get(slug, ""))
        if not cat:
            b = re.search(r'<div class="breadcrumb">.*?</a>.*?<a[^>]*>(.*?)</a>', s, re.S)
            cat = cat_slug(html.unescape(b.group(1))) if b else None
        cat = cat or "memory-brain"
        img = f"assets/img/{slug}.jpg"
        w, h = 900, 600
        if not os.path.exists(img):
            img = None
        elif Image:
            try:
                w, h = Image.open(img).size
            except Exception:
                pass
        alt = ""
        a = re.search(r'class="article-hero"[^>]*alt="([^"]*)"', s) or re.search(r'<img[^>]*class="article-hero"[^>]*>', s)
        if a and a.groups():
            alt = html.unescape(a.group(1))
        posts.append(dict(slug=slug, title=title, desc=desc, date=date, cat=cat, img=img, w=w, h=h, alt=alt or title))
    posts.sort(key=lambda x: (x["date"], x["slug"]), reverse=True)
    return posts


# ---------------------------------------------------------------- chrome
def header_html(active_cats):
    # every section is listed, even before its first article (its hub says so)
    nav = (['<a href="/">Home</a>'] + [f'<a href="/topics/{s}/">{esc(l)}</a>' for s, l, _ in CATS]
           + ['<a href="/memory-test/">Memory Test</a>', '<a href="/best-memory-supplements-2026/">Best of 2026</a>'])
    return (
        '<header class="mlh">\n'
        '  <div class="mlh-bar">\n'
        '    <div class="mlh-left">\n'
        '      <button class="mlh-menu" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>\n'
        '      <button class="ico-search mlh-search" aria-label="Search"><span class="mlh-ph">Search health topics</span>'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg></button>\n'
        '    </div>\n'
        '    <a class="mlh-logo" href="/">Memory <b>Lab</b> Daily</a>\n'
        '    <div class="mlh-right"><a class="mlh-cta" href="/memory-test/">Free Memory Test</a></div>\n'
        '  </div>\n'
        f'  <nav class="mlh-nav" aria-label="Sections"><div class="mlh-nav-in">{"".join(nav)}</div></nav>\n'
        '</header>'
    )


RE_TOPBAR = re.compile(r'<!-- TOP ANNOUNCEMENT BAR -->\s*|<div class="topbar">.*?</div></div>\s*', re.S)
RE_FTC = re.compile(r'<div class="ftc">.*?</div></div>\s*', re.S)
RE_OLDHEAD = re.compile(r'<header class="header">.*?</nav>\s*(?:<nav id="topic-hubs".*?</nav>\s*)?', re.S)
RE_NEWHEAD = re.compile(r'<header class="mlh">.*?</header>\s*', re.S)
SCRIPT = '<script src="/assets/chrome.js" defer></script>'


def apply_chrome(path, head):
    s = open(path, encoding="utf-8").read()
    o = s
    ftc = RE_FTC.search(s)
    ftc_html = ftc.group(0).strip() if ftc else ""
    s = RE_TOPBAR.sub("", s)
    s = RE_FTC.sub("", s)
    block = head + "\n" + (ftc_html + "\n" if ftc_html else "") + "\n"
    if RE_NEWHEAD.search(s):
        s = RE_NEWHEAD.sub(lambda m: block, s, count=1)
    elif RE_OLDHEAD.search(s):
        s = RE_OLDHEAD.sub(lambda m: block, s, count=1)
    else:
        return False
    if path.split("/")[0] in NO_ASIDE:
        s = s.replace('\n  <nav class="ml-toc" aria-label="In this article"></nav>', "")
        s = re.sub(r'\n  <aside class="ml-aside" aria-label="Latest"></aside>', "", s)
        s = s.replace('<main class="ml-main">', "<main>", 1)
    elif '<article class="article">' in s:
        s = s.replace("<main>", '<main class="ml-main">', 1)
        if 'class="ml-toc"' not in s:
            s = s.replace('<main class="ml-main">', '<main class="ml-main">\n  <nav class="ml-toc" aria-label="In this article"></nav>', 1)
        if 'class="ml-aside"' not in s:
            s = re.sub(r"(</article>)(\s*</main>)", r'\1\n  <aside class="ml-aside" aria-label="Latest"></aside>\2', s, count=1)
    # Photo credit: never under the hero. CC0/public domain need none, so it goes;
    # CC BY / BY-SA require attribution, so it moves to the end of the article.
    m = re.search(r'\s*<p class="img-credit">.*?</p>', s, re.S)
    if m and "</article>" in s:
        credit = m.group(0).strip()
        s = s[:m.start()] + s[m.end():]
        if not re.search(r"/ (CC0|Public domain)</p>$", credit, re.I):
            credit = credit.replace('<p class="img-credit">Photo:', '<p class="img-credit end">Image:', 1)
            s = s.replace("</article>", "  " + credit + "\n  </article>", 1)
    if SCRIPT not in s:
        s = s.replace("</body>", SCRIPT + "\n</body>", 1)
    if s != o:
        open(path, "w", encoding="utf-8").write(s)
        return True
    return False


# ---------------------------------------------------------------- home pieces
def img_tag(p, lazy=True, cls=""):
    if not p["img"]:
        return '<div class="noimg"></div>'
    return (f'<img{(" class=" + chr(34) + cls + chr(34)) if cls else ""} src="/{p["img"]}" width="{p["w"]}" height="{p["h"]}" '
            f'alt="{esc(p["alt"])}"{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""}>')


def url(p):
    return f'/{p["slug"]}/'


def cat_tag(p):
    return f'<a class="k" href="/topics/{p["cat"]}/">{esc(CAT_LABEL[p["cat"]])}</a>'


def card(p, rel=None):
    r = f'<a class="rel" href="{url(rel)}">{esc(rel["title"])}</a>' if rel else ""
    return (f'<div class="cd"><a class="cd-img" href="{url(p)}">{img_tag(p)}</a>{cat_tag(p)}'
            f'<h3><a href="{url(p)}">{esc(p["title"])}</a></h3>{r}</div>')


def hero(posts):
    P = posts + [None] * 20
    lead = P[0]
    rel = [x for x in P[1:4] if x]
    mini = [x for x in P[4:7] if x]
    # extra stories/thumbs stay hidden until chrome.js sees room for them,
    # so the three columns end level on any screen width
    mid = [x for x in P[7:15] if x]
    midrel = [x for x in P[15:23] if x]
    side = [x for x in P[23:31] if x]
    out = ['<section class="hx">', '<div class="hx-a">']
    if lead:
        out.append(f'<a class="hx-lead" href="{url(lead)}">{img_tag(lead, lazy=False)}<div class="hx-ov"><span>{esc(CAT_LABEL[lead["cat"]])}</span><h2>{esc(lead["title"])}</h2></div></a>')
    out.append('<ul class="rels">' + "".join(f'<li><a href="{url(x)}">{esc(x["title"])}</a></li>' for x in rel) + "</ul>")
    out.append('<div class="hx-mini">' + "".join(f'<div>{cat_tag(x)}<h3><a href="{url(x)}">{esc(x["title"])}</a></h3></div>' for x in mini) + "</div>")
    out.append("</div>")
    out.append('<div class="hx-b">')
    for i, x in enumerate(mid):
        r = midrel[i] if i < len(midrel) else None
        out.append(f'<div class="st">{cat_tag(x)}<h3><a href="{url(x)}">{esc(x["title"])}</a></h3>'
                   + (f'<a class="rel" href="{url(r)}">{esc(r["title"])}</a>' if r else "") + "</div>")
    out.append("</div>")
    out.append('<div class="hx-c">' + "".join(
        f'<a class="th" href="{url(x)}">{img_tag(x)}<div><span>{esc(CAT_LABEL[x["cat"]])}</span><h3>{esc(x["title"])}</h3></div></a>' for x in side) + "</div>")
    out.append("</section>")
    used = {x["slug"] for x in P[:31] if x}
    return "\n".join(out), used


def picks_row(posts):
    by = {p["slug"]: p for p in posts}
    ps = [by[s] for s in PICKS if s in by]
    if not ps:
        return ""
    tools = ('<aside class="tools"><h3>Free tools</h3>'
             '<a href="/memory-test/"><b>How sharp is your memory?</b><span>Take the free 3-minute test</span></a>'
             '<a href="/best-memory-supplements-2026/"><b>Best memory formulas of 2026</b><span>Our independent ranking</span></a>'
             '<a href="/editorial-policy/"><b>How we research</b><span>Our editorial policy</span></a></aside>')
    return ('<section class="sec"><h2 class="sh">Editors’ picks</h2><div class="row-tools">'
            '<div class="grid g4">' + "".join(card(p) for p in ps[:3]) + "</div>" + tools + "</div></section>")


def sections(posts, used):
    out = []
    for slug, label, _ in CATS:
        items = [p for p in posts if p["cat"] == slug]
        if not items:
            continue
        fresh = [p for p in items if p["slug"] not in used] or items
        show = fresh[:5]
        rest = [p for p in items if p not in show]
        cards = []
        for i, p in enumerate(show):
            cards.append(card(p, rest[i] if i < len(rest) else None))
        out.append(f'<section class="sec"><h2 class="sh"><a href="/topics/{slug}/">{esc(label)}</a>'
                   f'<a class="all" href="/topics/{slug}/">See all →</a></h2><div class="grid g5">{"".join(cards)}</div></section>')
    return "\n".join(out)


# ---------------------------------------------------------------- pages
def split_index():
    s = open("index.html", encoding="utf-8").read()
    head = s[: s.index("<body>") + len("<body>")]
    tail = s[s.index('<div class="disclaimer">'):]
    return head, tail


def set_meta(head, title, desc, canon):
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canon}">', head)
    head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canon}">', head)
    head = head.replace('href="assets/', 'href="/assets/')
    return head


HOME_TITLE = "Memory Lab — Independent Health, Memory & Wellness Guides"
HOME_DESC = "Independent, plain-English guides and reviews on memory, sleep, heart, gut and healthy aging."


def build_home(posts, head_html, tail):
    head, _ = split_index()
    head = set_meta(head, HOME_TITLE, HOME_DESC, SITE + "/")
    hx, used = hero(posts)
    body = (f"\n{head_html}\n\n<main class=\"home2\">\n<h1 class=\"sr-only\">Memory Lab: independent health, memory and wellness news, guides and reviews</h1>\n"
            f"{hx}\n{picks_row(posts)}\n{sections(posts, used)}\n</main>\n\n")
    tail = tail.replace('src="assets/', 'src="/assets/')
    open("index.html", "w", encoding="utf-8").write(head + body + tail)


def build_topics(posts, head_html, tail):
    head, _ = split_index()
    urls = []
    for slug, label, desc in CATS:
        items = [p for p in posts if p["cat"] == slug]
        canon = f"{SITE}/topics/{slug}/"
        h = set_meta(head, f"{label} — Memory Lab", desc, canon)
        if not items:
            # listed in the nav before its first article: noindex, show the latest posts
            h = h.replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex, follow">')
            body = (f"\n{head_html}\n\n<main class=\"home2\">\n"
                    f'<div class="tp-head"><div class="crumb"><a href="/">Home</a> › {esc(label)}</div><h1>{esc(label)}</h1><p>{esc(desc)}</p></div>\n'
                    f'<p class="tp-soon">The first {esc(label)} articles are being published this week. Meanwhile, here is the latest from Memory Lab.</p>\n'
                    f'<section class="sec"><div class="grid g5">{"".join(card(p) for p in posts[:10])}</div></section>\n</main>\n\n')
            os.makedirs(f"topics/{slug}", exist_ok=True)
            open(f"topics/{slug}/index.html", "w", encoding="utf-8").write(h + body + tail.replace('src="assets/', 'src="/assets/'))
            continue
        lead, rest = items[0], items[1:]
        body = (f"\n{head_html}\n\n<main class=\"home2\">\n"
                f'<div class="tp-head"><div class="crumb"><a href="/">Home</a> › {esc(label)}</div><h1>{esc(label)}</h1><p>{esc(desc)}</p></div>\n'
                f'<section class="tp-lead"><a class="hx-lead" href="{url(lead)}">{img_tag(lead, lazy=False)}<div class="hx-ov"><span>{esc(label)}</span><h2>{esc(lead["title"])}</h2></div></a>'
                f'<div class="tp-lead-txt"><p>{esc(lead["desc"])}</p><a class="more" href="{url(lead)}">Read the article →</a></div></section>\n'
                f'<section class="sec"><div class="grid g5">{"".join(card(p) for p in rest)}</div></section>\n</main>\n\n')
        os.makedirs(f"topics/{slug}", exist_ok=True)
        open(f"topics/{slug}/index.html", "w", encoding="utf-8").write(h + body + tail.replace('src="assets/', 'src="/assets/'))
        urls.append(canon)
    return urls


def sitemap_add(urls):
    if not os.path.exists("sitemap.xml"):
        return
    s = open("sitemap.xml", encoding="utf-8").read()
    add = "".join(f"  <url>\n    <loc>{u}</loc>\n    <changefreq>daily</changefreq>\n    <priority>0.6</priority>\n  </url>\n"
                  for u in urls if f"<loc>{u}</loc>" not in s)
    if add:
        s = s.replace("</urlset>", add + "</urlset>")
        open("sitemap.xml", "w", encoding="utf-8").write(s)


def main():
    posts = load_posts()
    active = [s for s, _, _ in CATS if any(p["cat"] == s for p in posts)]
    head_html = header_html(active)
    _, tail = split_index()
    if SCRIPT not in tail:
        tail = tail.replace("</body>", SCRIPT + "\n</body>", 1)
    build_home(posts, head_html, tail)
    topic_urls = build_topics(posts, head_html, tail)
    changed = 0
    for p in glob.glob("*/index.html"):
        if p.split("/")[0] in ("topics",):
            continue
        changed += apply_chrome(p, head_html)
    latest = [{"t": p["title"], "u": url(p), "c": CAT_LABEL[p["cat"]], "i": "/" + p["img"] if p["img"] else ""} for p in posts[:8]]
    json.dump(latest, open("assets/latest.json", "w"), ensure_ascii=False)
    sitemap_add(topic_urls)
    print(f"OK site: {len(posts)} posts, sections={','.join(active)}, chrome updated on {changed} pages, {len(topic_urls)} topic hubs")


if __name__ == "__main__":
    main()
