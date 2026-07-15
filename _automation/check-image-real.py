#!/usr/bin/env python3
"""
Reject synthetic / placeholder images before publishing.

A real photograph has macro-STRUCTURE (subjects, edges that survive downscaling)
AND many distinct colors. Synthetic junk fails one or both:
  - flat colors / gradients          -> no structure once you shrink away the grain
  - "natural grain texture" fills    -> looks busy at full size, collapses when shrunk
  - abstract bubble/circle renders    -> low structure, sometimes few colors
  - clip-art / vector pills          -> very few colors, hard flat edges

The old gate measured full-res adjacent-pixel diff ("edge energy"), which grain
and checkerboards PASS (noise = high local diff). It was fooled repeatedly. This
version shrinks to 24x24 first (killing per-pixel noise) and measures edge energy
on the DOWNSCALED image, then also counts distinct colors. Real photos keep
structure after the shrink; noise/gradient/flat/clip-art do not.

Usage:
  python3 _automation/check-image-real.py assets/img/<slug>.jpg
  python3 _automation/check-image-real.py --audit        # scan every image

Exit 0 = OK (real photo), 1 = FAIL (synthetic/junk). Prints OK/FAIL per file.
"""
import sys, glob
from PIL import Image

STRUCT_MIN = 6.0    # structural edge energy on 24x24 (below = flat/gradient/junk)
COLOR_MIN  = 800    # distinct colors in a 64x64 sample (below = clip-art / vector)

def structure(im):
    g = im.convert("L").resize((24, 24), Image.BILINEAR)
    px = list(g.getdata()); W = 24; tot = 0; n = 0
    for y in range(W):
        row = px[y*W:(y+1)*W]
        for x in range(1, W):
            tot += abs(row[x] - row[x-1]); n += 1
        if y > 0:
            for x in range(W):
                tot += abs(px[y*W+x] - px[(y-1)*W+x]); n += 1
    return tot / n

def color_count(im):
    return len(set(im.convert("RGB").resize((64, 64), Image.BILINEAR).getdata()))

def check(fp):
    try:
        im = Image.open(fp)
    except Exception as ex:
        print(f"FAIL  {fp}  (cannot open: {ex})"); return False
    s = structure(im); c = color_count(im)
    ok = s >= STRUCT_MIN and c >= COLOR_MIN
    why = "" if ok else f"  <- {'flat/gradient/grain' if s < STRUCT_MIN else 'clip-art/few-colors'}"
    print(f"{'OK  ' if ok else 'FAIL'}  {fp}  (structure={s:.2f}/{STRUCT_MIN}, colors={c}/{COLOR_MIN}){why}")
    return ok

if __name__ == "__main__":
    if "--audit" in sys.argv:
        bad = 0
        for fp in sorted(glob.glob("assets/img/*.jpg")):
            if not check(fp): bad += 1
        print(f"\n{'OK' if bad == 0 else 'FAIL'}: {bad} synthetic/junk image(s) found.")
        sys.exit(1 if bad else 0)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: check-image-real.py <img.jpg> | --audit"); sys.exit(2)
    sys.exit(0 if all(check(a) for a in args) else 1)
