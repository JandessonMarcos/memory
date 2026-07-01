#!/usr/bin/env python3
"""
Image de-duplication guard for the Memory Lab daily routine.

The routine MUST call this before saving any new article image, so the same
stock photo never lands on two posts (a real problem we hit: one lab photo on
5 posts, one "woman at laptop" on 3, etc.).

Uses a 12x12 average-hash (144 bits) via Pillow only (no extra deps).
Two images are considered "the same visual" when their Hamming distance is
<= THRESHOLD bits. Default threshold 12 catches exact dupes AND re-crops /
re-compressions of the same source photo.

Usage:
  # Guard one candidate before saving it as assets/img/<slug>.jpg:
  python3 _automation/check-image-unique.py /tmp/candidate.jpg [--slug <slug>] [--threshold N]
    -> exit 0 + "PASS" if visually distinct from everything already in assets/img/
    -> exit 1 + names the closest existing image if it collides (RE-SOURCE it)

  # Audit the whole folder (find existing duplicate groups):
  python3 _automation/check-image-unique.py --audit [--threshold N]
    -> exit 0 if all unique, exit 1 and prints every duplicate group otherwise
"""
import sys, os, glob

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("Pillow missing: pip install --quiet Pillow\n")
    sys.exit(2)

HASH_SIDE = 12
DEFAULT_THRESHOLD = 12
IMG_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "img"))


def ahash(path, side=HASH_SIDE):
    im = Image.open(path).convert("L").resize((side, side))
    px = list(im.getdata())
    avg = sum(px) / len(px)
    bits = 0
    for i, v in enumerate(px):
        if v > avg:
            bits |= (1 << i)
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


def existing_hashes(exclude_basename=None):
    out = {}
    for f in sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg"))):
        b = os.path.basename(f)
        if exclude_basename and b == exclude_basename:
            continue
        try:
            out[b] = ahash(f)
        except Exception as e:
            sys.stderr.write(f"skip {b}: {e}\n")
    return out


def guard(candidate, slug, threshold):
    if not os.path.isfile(candidate):
        sys.stderr.write(f"no such file: {candidate}\n")
        return 2
    exclude = f"{slug}.jpg" if slug else None
    ch = ahash(candidate)
    closest, best = None, 999
    for name, h in existing_hashes(exclude_basename=exclude).items():
        d = hamming(ch, h)
        if d < best:
            best, closest = d, name
    if closest is not None and best <= threshold:
        print(f"FAIL  too similar to {closest} (distance {best} <= {threshold}). RE-SOURCE a different photo.")
        return 1
    where = f" (closest existing: {closest}, distance {best})" if closest else ""
    print(f"PASS  visually distinct{where}")
    return 0


def audit(threshold):
    H = existing_hashes()
    names = list(H)
    seen, groups = set(), []
    for i, a in enumerate(names):
        if a in seen:
            continue
        g = [a]
        for b in names[i + 1:]:
            if b in seen:
                continue
            if hamming(H[a], H[b]) <= threshold:
                g.append(b)
                seen.add(b)
        if len(g) > 1:
            seen.add(a)
            groups.append(g)
    if not groups:
        print(f"OK  {len(names)} images, all visually unique (threshold {threshold}).")
        return 0
    print(f"DUPLICATES  {len(names)} images, {len(groups)} colliding group(s):")
    for g in sorted(groups, key=len, reverse=True):
        print(f"  [{len(g)}x] " + "  ".join(s.replace('.jpg', '') for s in g))
    return 1


def main(argv):
    threshold = DEFAULT_THRESHOLD
    slug = None
    positional = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--threshold":
            threshold = int(argv[i + 1]); i += 2; continue
        if a == "--slug":
            slug = argv[i + 1]; i += 2; continue
        positional.append(a); i += 1
    if positional and positional[0] == "--audit":
        return audit(threshold)
    if not positional:
        sys.stderr.write(__doc__)
        return 2
    return guard(positional[0], slug, threshold)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
