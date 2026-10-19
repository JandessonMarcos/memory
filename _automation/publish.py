#!/usr/bin/env python3
"""
Refresh the sitemap and search index, mark the queue done, then rebuild the home,
section hubs and shared header with site.py. Run after gen-post.py +
source-image.py, before the image gates.

  python3 _automation/publish.py <slug> [<slug> ...]      # last listed = newest
"""
import sys, os, re, json
from PIL import Image

SITE = "https://www.memorylabdaily.com"
LATEST_CAP = 4
SECTION = {
    "Memory": "Memory &amp; brain health",
    "Brain Health": "Memory &amp; brain health",
    "Aging Well": "Memory &amp; brain health",
    "Ingredients": "Ingredients &amp; evidence",
    "Reviews": "Reviews &amp; comparisons",
}


def card(slug, spec):
    w, h = Image.open(f"assets/img/{slug}.jpg").size
    return (
        f'    <a class="post-card" href="{slug}/">\n'
        f'      <div class="post-thumb t1"><img width="{w}" height="{h}" '
        f'src="assets/img/{slug}.jpg" alt="{spec["alt"]}" loading="lazy"></div>\n'
        f'      <div class="pc-body">\n'
        f'        <span class="pc-cat">{spec["cat"]}</span>\n'
        f'        <h3>{spec["og_title"]}</h3>\n'
        f'        <p>{spec["desc"]}</p>\n'
        f'        <span class="pc-more">Read more &rarr;</span>\n'
        f'      </div>\n'
        f'    </a>\n')


def grid_bounds(html, label):
    """Return (start, end) offsets of the card-grid contents for a section."""
    m = re.search(r'<p class="section-label">' + re.escape(label) +
                  r'</p>\s*\n\s*<div class="card-grid">', html)
    if not m:
        raise SystemExit(f"section not found: {label}")
    start = m.end()
    depth, i = 1, start
    while depth:
        nxt = re.search(r'<div\b|</div>', html[i:])
        if not nxt:
            raise SystemExit(f"unbalanced card-grid in {label}")
        i += nxt.end()
        depth += 1 if nxt.group() == "<div" else -1
    return start, i - len("</div>")


def cards_in(block):
    return re.findall(r'    <a class="post-card".*?\n    </a>\n', block, re.S)


def drop_slug(html, slug):
    """Remove any existing card for slug, anywhere on the page."""
    return re.sub(r'    <a class="post-card" href="' + re.escape(slug) +
                  r'/">.*?\n    </a>\n', "", html, flags=re.S)


def main(slugs):
    specs = {s: json.load(open(f"_automation/posts/{s}.json")) for s in slugs}

    # The home is no longer edited card by card: site.py rebuilds it (and the
    # section hubs) from the articles themselves at the end of this script.

    # Sitemap: append any missing URL next to the existing entries.
    sm = open("sitemap.xml").read()
    added = 0
    for slug in slugs:
        url = f"{SITE}/{slug}/"
        if url in sm:
            continue
        entry = (f"  <url>\n    <loc>{url}</loc>\n"
                 f"    <lastmod>{specs[slug]['date']}</lastmod>\n"
                 f"    <changefreq>monthly</changefreq>\n"
                 f"    <priority>0.7</priority>\n  </url>\n")
        sm = sm.replace("</urlset>", entry + "</urlset>")
        added += 1
    open("sitemap.xml", "w").write(sm)

    # Queue: mark published.
    qf = "_automation/content-queue.json"
    q = json.load(open(qf))
    done = 0
    kws = {}
    for item in q["queue"]:
        if item["slug"] in specs:
            kws[item["slug"]] = item.get("kw", "")
            if item.get("status") != "done":
                item["status"] = "done"
                item["published"] = specs[item["slug"]]["date"]
                done += 1
    json.dump(q, open(qf, "w"), indent=2, ensure_ascii=False)

    # Site search index. The routine added assets/search-index.json in an earlier
    # run but never wired it into this script, so posts published here were
    # silently missing from on-site search. Keep it in step automatically.
    sif = "assets/search-index.json"
    try:
        idx = json.load(open(sif))
    except Exception:
        idx = []
    have = {e.get("u") for e in idx}
    sadded = 0
    for slug in slugs:
        u = f"/{slug}/"
        if u in have:
            continue
        spec = specs[slug]
        idx.append({"t": spec["og_title"], "u": u, "c": spec["cat"],
                    "k": kws.get(slug, ""), "d": spec["desc"]})
        sadded += 1
    json.dump(idx, open(sif, "w"), indent=2, ensure_ascii=False)

    print(f"sitemap: +{added} | queue: {done} marked done | search-index: +{sadded}")
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "site.py")], check=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
