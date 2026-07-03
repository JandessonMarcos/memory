#!/usr/bin/env python3
"""
Reject flat/gradient/placeholder images before publishing.

A real photograph has high local detail (edges, texture). A flat color, a
smooth gradient, or an abstract render has almost none. We measure the mean
absolute difference between adjacent grayscale pixels ("edge energy"): real
photos score well above ~3; flat gradients score below ~2.

Usage:
  python3 _automation/check-image-real.py assets/img/<slug>.jpg
  python3 _automation/check-image-real.py --audit        # scan every image

Exit code 0 = OK (real photo), 1 = FAIL (flat/gradient/junk). Prints OK/FAIL.
"""
import sys, glob, os
from PIL import Image

THRESHOLD = 3.0  # below this = flat/gradient/junk

def edge_energy(fp):
    im = Image.open(fp).convert("L").resize((200, 200))
    px = list(im.getdata()); W = 200; tot = 0; n = 0
    for y in range(W):
        row = px[y*W:(y+1)*W]
        for x in range(1, W):
            tot += abs(row[x] - row[x-1]); n += 1
    return tot / n

def check(fp):
    try:
        e = edge_energy(fp)
    except Exception as ex:
        print(f"FAIL  {fp}  (cannot open: {ex})"); return False
    ok = e >= THRESHOLD
    print(f"{'OK  ' if ok else 'FAIL'}  {fp}  (edge_energy={e:.2f}, need >= {THRESHOLD})")
    return ok

if __name__ == "__main__":
    if "--audit" in sys.argv:
        bad = 0
        for fp in sorted(glob.glob("assets/img/*.jpg")):
            if not check(fp): bad += 1
        print(f"\n{'OK' if bad == 0 else 'FAIL'}: {bad} flat/gradient image(s) found.")
        sys.exit(1 if bad else 0)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: check-image-real.py <img.jpg> | --audit"); sys.exit(2)
    sys.exit(0 if all(check(a) for a in args) else 1)
