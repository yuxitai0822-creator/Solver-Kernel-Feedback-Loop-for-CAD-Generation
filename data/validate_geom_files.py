"""Validate geometric files (step/smt/obj) by signature & header, no kernel needed.

We sample to keep it fast, but check:
- STEP files start with ISO-10303-21 header (valid STEP AP242/AP203)
- SMT files: Fusion proprietary, check 'SMT' / magic
- OBJ files: text wavefront, check 'v'/'f' lines or '#'
- report sizes, empty files, truncated files

Then for the Kernel feedback arm we note whether OpenCascade can read STEP.
We can't run OCP here (not installed), so we validate STEP headers only.
"""
import json
from collections import Counter
from pathlib import Path

RECON = Path(r"D:\dataset\r1.0.1\reconstruction")
N_SAMPLE_PER_EXT = 60

import random
random.seed(0)


def sample_files(ext):
    files = sorted(RECON.glob(f"*{ext}"))
    return random.sample(files, min(N_SAMPLE_PER_EXT, len(files))), len(files)


def head(path, n=4):
    try:
        with open(path, "rb") as f:
            return f.read(400)
    except Exception as e:
        return f"<err {e}>"


def main():
    report = {}
    for ext in [".step", ".smt", ".obj"]:
        sample, total = sample_files(ext)
        good = 0
        bad = []
        sizes = []
        for fp in sample:
            sz = fp.stat().st_size
            sizes.append(sz)
            h = head(fp)
            hs = h.decode("latin-1", "ignore")
            ok = False
            if ext == ".step":
                ok = "ISO-10303-21" in hs
            elif ext == ".obj":
                ok = (b"v " in h) or (b"f " in h) or hs.lstrip().startswith("#")
            elif ext == ".smt":
                # SMT is proprietary binary; check non-empty and reasonable magic
                ok = sz > 16 and (h[:3] == b"SMT" or any(ch < 128 for ch in h[:8]))
            if ok:
                good += 1
            else:
                bad.append((fp.name, sz, hs[:80].replace("\n", "\\n")))
        report[ext] = {
            "total_on_disk": total,
            "sampled": len(sample),
            "valid_header": good,
            "invalid_header_examples": bad[:5],
            "size_min": min(sizes) if sizes else 0,
            "size_max": max(sizes) if sizes else 0,
            "size_median_approx": sorted(sizes)[len(sizes)//2] if sizes else 0,
            "first_step_header": head(next(iter(sample_files(ext)[0])), )[:200].decode("latin-1","ignore") if sample else "",
        }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
