#!/usr/bin/env python3
"""
Build / refill the offline hero-image POOL (source: Wikimedia Commons).

WHY THIS EXISTS: the cloud routine's sandbox blocks egress to api.openverse.org
(403 CONNECT, org egress policy), so source-image.py cannot fetch a fresh hero
in the cloud. This builder runs LOCALLY (where the internet works) and stockpiles
a library of vetted, real, unique freely-licensed photos under assets/img-pool/,
each tagged with themes in _automation/img-pool.json. In the cloud, source-image.py
falls back to this pool (zero network) when Openverse is unreachable.

Source is Wikimedia Commons rather than Openverse because Commons has a far more
generous rate limit for bulk fetching (Openverse throttles anonymous bulk hard,
429). Every Commons file is freely licensed; we still record license + author in
the manifest so the fallback path stays attribution-compliant.

Run locally to build or top up the pool:
  python3 _automation/build-pool.py            # top up toward the per-theme target (6)
  python3 _automation/build-pool.py --target 8 # aim for N usable images per theme

Validates every image with the SAME real-photo + uniqueness gates as
source-image.py, and guarantees pool images don't collide with each other or with
any hero already in assets/img/.
"""
import sys, os, io, glob, json, time, urllib.request, urllib.parse
from PIL import Image

# Wikimedia asks for a descriptive UA identifying the app + contact.
UA = {"User-Agent": "MemoryLabDaily/1.0 (https://www.memorylabdaily.com; hero-image pool builder)"}
IMG_DIR = "assets/img"
POOL_DIR = "assets/img-pool"
MANIFEST = "_automation/img-pool.json"
API = "https://commons.wikimedia.org/w/api.php"
STRUCT_MIN = 9.0
COLOR_MIN  = 1200
HAM_MIN    = 10

THEMES = {
    "brain-science":     ["human brain anatomy", "neuron nerve cell", "brain mri scan", "brain diagram model"],
    "senior-aging":      ["elderly woman portrait", "senior man outdoors", "old couple walking", "grandmother gardening", "senior citizen smiling"],
    "food-nutrition":    ["fresh vegetables", "healthy salad", "blueberries fruit", "salmon dish", "nuts walnuts"],
    "exercise-fitness":  ["person jogging", "woman yoga", "senior exercise", "people walking outdoors", "nordic walking", "woman running outdoor", "cycling outdoors", "gym dumbbell workout", "elderly couple walking"],
    "sleep-rest":        ["person sleeping", "bedroom bed", "woman resting", "man sleeping bed", "woman sleeping pillow", "napping sofa", "bedroom interior morning"],
    "study-focus":       ["student studying", "woman reading book", "person laptop working", "library books", "woman studying laptop", "man reading newspaper", "reading glasses book", "college student writing", "desk workspace laptop"],
    "supplement-pills":  ["dietary supplement capsules", "vitamin pills", "medicine tablets", "fish oil capsules", "pills close up", "medication bottle", "pharmacy tablets", "colorful pills"],
    "doctor-medical":    ["doctor patient", "nurse blood pressure", "stethoscope", "medical checkup"],
    "nature-lifestyle":  ["forest path walking", "sunrise landscape", "green tea cup", "coffee cup table"],
    "meditation-calm":   ["woman meditation", "yoga meditation", "person relaxing outdoors"],
    "social-connection": ["friends together", "family dinner", "elderly people group", "people talking cafe"],
    "thinking-memory":   ["person thinking", "jigsaw puzzle pieces", "chess board", "sticky notes wall", "notebook writing"],
}

def structure(im):
    g = im.convert("L").resize((24, 24), Image.BILINEAR)
    px = list(g.getdata()); W = 24; tot = 0; n = 0
    for y in range(W):
        row = px[y*W:(y+1)*W]
        for x in range(1, W): tot += abs(row[x]-row[x-1]); n += 1
        if y > 0:
            for x in range(W): tot += abs(px[y*W+x]-px[(y-1)*W+x]); n += 1
    return tot / n

def color_count(im):
    return len(set(im.convert("RGB").resize((64, 64), Image.BILINEAR).getdata()))

def ahash(im):
    g = im.convert("L").resize((12, 12), Image.BILINEAR)
    px = list(g.getdata()); a = sum(px)/len(px)
    return [1 if p > a else 0 for p in px]

def ham(a, b): return sum(x != y for x, y in zip(a, b))

def valid(im):
    w, h = im.size
    return (w >= 600 and h >= 380 and 0.95 <= w/h <= 2.4
            and im.mode not in ("RGBA", "LA", "P")
            and structure(im) >= STRUCT_MIN and color_count(im) >= COLOR_MIN)

def all_hashes():
    out = []
    for fp in glob.glob(os.path.join(IMG_DIR, "*.jpg")) + glob.glob(os.path.join(POOL_DIR, "*.jpg")):
        try: out.append(ahash(Image.open(fp)))
        except Exception: pass
    return out

def load_manifest():
    if os.path.exists(MANIFEST):
        return json.load(open(MANIFEST))
    return {"_comment": "Offline hero-image pool. Built by build-pool.py (Wikimedia Commons), consumed by source-image.py when Openverse egress is blocked. used_by=null means available.", "images": []}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)

def search(q):
    """Return list of (thumburl, license, author, descurl) for photo files matching q."""
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": q, "gsrnamespace": "6", "gsrlimit": "30",
        "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": "1200",
    }
    d = json.load(get(API + "?" + urllib.parse.urlencode(params)))
    out = []
    pages = (d.get("query") or {}).get("pages") or {}
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        mime = ii.get("mime", "")
        if mime != "image/jpeg":
            continue
        thumb = ii.get("thumburl")
        if not thumb:
            continue
        em = ii.get("extmetadata") or {}
        lic = (em.get("LicenseShortName") or {}).get("value", "")
        author = (em.get("Artist") or {}).get("value", "")
        # strip html tags from author
        import re as _re
        author = _re.sub("<[^>]+>", "", author).strip()
        out.append((thumb, lic, author, ii.get("descriptionurl", "")))
    return out

def build(target):
    os.makedirs(POOL_DIR, exist_ok=True)
    man = load_manifest()
    have = man["images"]
    seen = {e.get("src") for e in have}
    hashes = all_hashes()
    per_theme = {}
    for e in have:
        for t in e.get("themes", []):
            per_theme[t] = per_theme.get(t, 0) + 1

    added_total = 0
    for theme, queries in THEMES.items():
        need = target - per_theme.get(theme, 0)
        if need <= 0:
            print(f"[{theme}] has {per_theme.get(theme,0)} (>= {target}), skip"); continue
        added = 0
        for q in queries:
            if added >= need: break
            try:
                results = search(q)
            except Exception as e:
                print(f"  [{theme}] search err ({q}): {e}"); time.sleep(2); continue
            for thumb, lic, author, descurl in results:
                if added >= need: break
                if thumb in seen: continue
                try:
                    raw = get(thumb).read(); im = Image.open(io.BytesIO(raw))
                except Exception: continue
                if im.mode in ("RGBA", "LA", "P"): continue
                im = im.convert("RGB")
                if not valid(im): continue
                hsh = ahash(im)
                if any(ham(hsh, e) <= HAM_MIN for e in hashes): continue
                idx = len([e for e in have if theme in e.get("themes", [])]) + 1
                fn = f"{theme}-{idx:02d}.jpg"
                nh = int(im.size[1] * 900 / im.size[0])
                im.resize((900, nh), Image.LANCZOS).save(os.path.join(POOL_DIR, fn), "JPEG", quality=86)
                entry = {"file": fn, "themes": [theme], "kw": q, "license": lic or "Wikimedia Commons",
                         "attribution": (author or "Unknown") + " / Wikimedia Commons", "src": thumb, "descurl": descurl, "used_by": None}
                have.append(entry); seen.add(thumb); hashes.append(hsh)
                added += 1; added_total += 1
                print(f'  [{theme}] +{fn}  lic={lic}  <- "{q}"')
                time.sleep(0.3)
            time.sleep(0.5)
        per_theme[theme] = per_theme.get(theme, 0) + added
        print(f"[{theme}] added {added} (total {per_theme[theme]})")

    json.dump(man, open(MANIFEST, "w"), ensure_ascii=False, indent=1)
    print(f"\nDONE. Added {added_total} new pool images. Pool size = {len(have)}.")

if __name__ == "__main__":
    target = 6
    if "--target" in sys.argv:
        target = int(sys.argv[sys.argv.index("--target")+1])
    build(target)
