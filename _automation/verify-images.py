#!/usr/bin/env python3
"""
Pre-push image gate: every hero image a post *references* must actually EXIST
and be a real photo.

Why this exists: check-image-real.py and check-image-unique.py only audit files
that are already in assets/img/. They are blind to the exact failure that keeps
shipping — the routine generates <slug>/index.html referencing
`assets/img/<slug>.jpg` but never sources/commits the image, so the post goes
live with a broken image. This script closes that hole: it walks every article's
index.html, extracts the referenced hero image(s), and FAILS if any is missing
(or is synthetic junk by the same structure/color test as check-image-real).

Usage:
  python3 _automation/verify-images.py          # scan every article, exit 1 on any miss
Run this LAST, right before `git add`/commit. If it prints FAIL, source the
missing image with source-image.py — never commit around it.
"""
import sys, os, re, glob
from PIL import Image

STRUCT_MIN = 6.0     # same threshold as check-image-real.py
COLOR_MIN  = 800

IMG_RE = re.compile(r'(?:src|content)="(?:\.\./)*(assets/img/[a-z0-9-]+\.(?:jpg|jpeg|png|webp))"', re.I)

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

def is_real_photo(path):
    try:
        im = Image.open(path)
    except Exception as ex:
        return False, f"cannot open: {ex}"
    s = structure(im); c = color_count(im)
    if s < STRUCT_MIN: return False, f"flat/gradient/grain (structure={s:.1f}<{STRUCT_MIN})"
    if c < COLOR_MIN:  return False, f"clip-art/few-colors (colors={c}<{COLOR_MIN})"
    return True, f"structure={s:.1f} colors={c}"

def main():
    articles = sorted(glob.glob("*/index.html"))
    missing, junk, checked = [], [], 0
    for html in articles:
        try:
            with open(html, encoding="utf-8") as f:
                txt = f.read()
        except Exception:
            continue
        refs = {m.group(1) for m in IMG_RE.finditer(txt)}
        if not refs:
            continue
        for ref in sorted(refs):
            checked += 1
            if not os.path.isfile(ref):
                missing.append((html, ref)); continue
            ok, why = is_real_photo(ref)
            if not ok:
                junk.append((html, ref, why))
    for html, ref in missing:
        print(f"MISSING  {html}  ->  {ref}   (post references an image that does not exist)")
    for html, ref, why in junk:
        print(f"JUNK     {html}  ->  {ref}   ({why})")
    bad = len(missing) + len(junk)
    print(f"\n{'OK' if bad == 0 else 'FAIL'}: {checked} referenced hero image(s) checked, "
          f"{len(missing)} missing, {len(junk)} synthetic.")
    if bad:
        print("Fix: source each missing/junk slug with "
              "`python3 _automation/source-image.py <slug> \"concrete subject\" ...` before committing.")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
