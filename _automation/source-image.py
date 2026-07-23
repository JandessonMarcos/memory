#!/usr/bin/env python3
"""
Source a REAL Creative-Commons photo for a blog hero and install it.

This exists because the daily routine kept *inventing* hero images (PIL-drawn
gradients, grain textures, abstract bubble renders) whenever ad-hoc sourcing was
inconvenient. Those are banned. Image sourcing is now deterministic: call this
script with a slug and one or more CONCRETE subject queries; it fetches a real
photo from Openverse, validates it the same way check-image-real.py does
(structure + distinct colors), guarantees visual uniqueness across the blog, and
installs it resized to 900px wide.

Usage:
  python3 _automation/source-image.py <slug> "concrete subject" ["alt subject" ...]
  # e.g.
  python3 _automation/source-image.py salmon-and-memory "salmon fillet plate" "grilled salmon"

Prints "OK  <slug> ..." on success (file written to assets/img/<slug>.jpg),
or "MISS <slug>" if nothing passed. Exit 0 on success, 1 on miss/usage error.

Rules baked in (do NOT weaken):
  - Only cc0/pdm, then by/by-sa as a last resort (attribution-lighter first).
  - Reject rawpixel (watermarks), svg/png (clip-art/transparency), non-landscape,
    low-structure (gradient/grain), few-color (clip-art), and visual duplicates.
  - NEVER generate/draw an image. If this misses, add different concrete subjects.
"""
import sys, os, io, glob, json, time, urllib.request, urllib.parse
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (Macintosh) MemoryLab/1.0"}
IMG_DIR = "assets/img"
POOL_DIR = "assets/img-pool"                 # offline fallback pool (built by build-pool.py)
MANIFEST = "_automation/img-pool.json"       # pool manifest; used_by=null means available
STRUCT_MIN = 9.0     # structural edge energy on 24x24 (real photo territory)
COLOR_MIN  = 1200    # distinct colors in 64x64 (clip-art/monochrome fail)

# Map article keywords -> pool themes, so the offline fallback still picks an
# on-topic photo when Openverse egress is blocked (the cloud sandbox denies it).
THEME_HINTS = {
    "senior-aging":      ["senior", "elderly", "aging", "ageing", "older", "old age", "grandmother", "grandfather", "grandparent", "retire", "dementia", "alzheimer"],
    "food-nutrition":    ["food", "diet", "nutrition", "vegetable", "fruit", "berry", "berries", "salmon", "fish", "nut", "omega", "eat", "meal", "mediterranean", "curcumin", "turmeric", "quercetin", "choline", "green tea"],
    "exercise-fitness":  ["exercise", "walk", "walking", "run", "running", "jog", "fitness", "gym", "yoga", "workout", "physical activity", "active", "cardio", "movement", "strength"],
    "sleep-rest":        ["sleep", "rest", "insomnia", "nap", "bed", "night", "circadian", "tired", "fatigue"],
    "study-focus":       ["study", "studying", "read", "reading", "learn", "learning", "focus", "concentration", "attention", "student", "book", "desk", "productivity", "exam"],
    "supplement-pills":  ["supplement", "pill", "capsule", "vitamin", "dose", "dosage", "tablet", "medicine", "medication", "nootropic", "formula"],
    "doctor-medical":    ["doctor", "medical", "blood pressure", "hypertension", "blood sugar", "glucose", "diabetes", "nurse", "checkup", "clinic", "diagnosis", "cholesterol", "physician", "health screening"],
    "nature-lifestyle":  ["nature", "forest", "tea", "coffee", "outdoor", "outdoors", "sunrise", "lifestyle", "walk in nature", "fresh air"],
    "meditation-calm":   ["meditation", "meditate", "calm", "stress", "relax", "mindfulness", "breathing", "anxiety", "cortisol", "wellbeing", "mood"],
    "social-connection": ["social", "friend", "family", "connection", "lonely", "loneliness", "together", "people", "community", "relationship", "conversation"],
    "thinking-memory":   ["memory", "remember", "recall", "think", "thinking", "puzzle", "chess", "forget", "forgetful", "brain training", "brain game", "notes", "working memory", "cognition", "cognitive", "mental", "brain", "neuron", "neural", "cortex", "mri", "scan", "anatomy", "mind"],
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

def load_existing(skip_slug):
    out = []
    for fp in glob.glob(os.path.join(IMG_DIR, "*.jpg")):
        if os.path.basename(fp)[:-4] == skip_slug: continue
        try: out.append(ahash(Image.open(fp)))
        except Exception: pass
    return out

def valid(im):
    w, h = im.size
    return (w >= 600 and h >= 380 and 0.95 <= w/h <= 2.4
            and im.mode not in ("RGBA", "LA", "P")
            and structure(im) >= STRUCT_MIN and color_count(im) >= COLOR_MIN)

def source(slug, queries):
    existing = load_existing(slug)
    for lic in ["cc0,pdm", "by,by-sa"]:
        for q in queries:
            url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
                {"q": q, "license": lic, "size": "medium,large", "mature": "false", "page_size": "16"})
            try:
                d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25))
            except Exception as e:
                print(f"  query err ({q}/{lic}): {e}"); time.sleep(1); continue
            for r in d.get("results", []):
                iu = r.get("url") or ""
                if not iu or "rawpixel" in iu or iu.lower().endswith((".svg", ".png")): continue
                try:
                    raw = urllib.request.urlopen(urllib.request.Request(iu, headers=UA), timeout=25).read()
                    im = Image.open(io.BytesIO(raw))
                except Exception: continue
                if im.mode in ("RGBA", "LA", "P"): continue
                im = im.convert("RGB")
                if not valid(im): continue
                hsh = ahash(im)
                if any(ham(hsh, e) <= 10 for e in existing): continue
                nh = int(im.size[1] * 900 / im.size[0])
                out = os.path.join(IMG_DIR, slug + ".jpg")
                im.resize((900, nh), Image.LANCZOS).save(out, "JPEG", quality=86)
                print(f'OK  {slug}  struct={structure(im):.1f} colors={color_count(im)} '
                      f'lic={r.get("license")}  <- "{q}"  {iu[:60]}')
                return True
    print(f"MISS {slug}  (openverse: no real photo passed)")
    return False

def theme_scores(text):
    text = text.lower()
    scores = {}
    for theme, kws in THEME_HINTS.items():
        s = sum(text.count(k) for k in kws)
        if s:
            scores[theme] = s
    return scores

def pick_from_pool(slug, queries):
    """Offline fallback: install the best-matching unused pool image for this slug.
    Used when Openverse is unreachable (cloud egress block) or returns nothing."""
    if not os.path.exists(MANIFEST):
        print(f"POOL-MISS {slug}  (no pool manifest; run build-pool.py locally)"); return False
    man = json.load(open(MANIFEST))
    imgs = man.get("images", [])
    avail = [e for e in imgs if not e.get("used_by")]
    if not avail:
        print(f"POOL-MISS {slug}  (pool exhausted; refill locally with build-pool.py)"); return False
    text = slug.replace("-", " ") + " " + " ".join(queries)
    scores = theme_scores(text)
    existing = load_existing(slug)
    # best-scoring themes first, then every remaining theme as a last resort
    ordered = [t for t, _ in sorted(scores.items(), key=lambda kv: -kv[1])]
    for t in THEME_HINTS:
        if t not in ordered:
            ordered.append(t)
    for theme in ordered:
        for e in [x for x in avail if theme in x.get("themes", [])]:
            fp = os.path.join(POOL_DIR, e["file"])
            try:
                im = Image.open(fp).convert("RGB")
            except Exception:
                continue
            if any(ham(ahash(im), x) <= 10 for x in existing):
                continue  # never let one photo serve two slugs
            nh = int(im.size[1] * 900 / im.size[0])
            out = os.path.join(IMG_DIR, slug + ".jpg")
            im.resize((900, nh), Image.LANCZOS).save(out, "JPEG", quality=86)
            e["used_by"] = slug
            json.dump(man, open(MANIFEST, "w"), ensure_ascii=False, indent=1)
            print(f'OK  {slug}  (pool/{theme})  lic={e.get("license")}  attr="{e.get("attribution")}"  <- {e["file"]}')
            return True
    print(f"POOL-MISS {slug}  (no unique pool match left)"); return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: source-image.py <slug> "subject" ["alt subject" ...]'); sys.exit(1)
    slug = sys.argv[1]; queries = sys.argv[2:]
    ok = False
    try:
        ok = source(slug, queries)          # 1) try Openverse (fresh, bespoke)
    except Exception as e:
        print(f"  openverse path error: {e}")
    if not ok:
        print(f"  Openverse unavailable/miss -> falling back to offline pool")
        ok = pick_from_pool(slug, queries)  # 2) offline pool (works with no egress)
    sys.exit(0 if ok else 1)
