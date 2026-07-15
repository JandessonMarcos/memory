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
STRUCT_MIN = 9.0     # structural edge energy on 24x24 (real photo territory)
COLOR_MIN  = 1200    # distinct colors in 64x64 (clip-art/monochrome fail)

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
    print(f"MISS {slug}  (no real photo passed; add different concrete subject queries)")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: source-image.py <slug> "subject" ["alt subject" ...]'); sys.exit(1)
    slug = sys.argv[1]; queries = sys.argv[2:]
    sys.exit(0 if source(slug, queries) else 1)
