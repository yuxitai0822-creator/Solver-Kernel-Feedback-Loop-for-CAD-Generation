"""Profile the file modality distribution in reconstruction/.

For each file extension we count occurrences and total size. We also classify
files by their "root sequence id" (e.g. 133248_c7255340_0000 stripped of the
trailing _NNNN operation index) to understand the per-sequence structure.
"""
from collections import Counter, defaultdict
from pathlib import Path

RECON = Path(r"D:\dataset\r1.0.1\reconstruction")


def main():
    ext_count = Counter()
    ext_size = defaultdict(int)
    stems = Counter()  # full stem like 133248_c7255340_0000_0001
    seq_roots = Counter()  # 133248_c7255340_0000 part

    for p in RECON.iterdir():
        if not p.is_file():
            continue
        ext = p.suffix.lower() or "<none>"
        ext_count[ext] += 1
        ext_size[ext] += p.stat().st_size
        stems[p.stem] += 1
        # seq root: strip optional trailing _\d+ (operation sub-index)
        stem = p.stem
        parts = stem.split("_")
        # designid(=number)_hash(hex)_seq(4 digits)[_op(4 digits)]
        if len(parts) >= 3:
            root = "_".join(parts[:3])
            seq_roots[root] += 1

    print("=== file extension distribution ===")
    total_files = sum(ext_count.values())
    print(f"  total files: {total_files}")
    for ext, c in ext_count.most_common():
        mb = ext_size[ext] / 1024 / 1024
        print(f"  {ext:8s}: {c:>8d} files  ({mb:9.1f} MB)")

    print("\n=== per-sequence file counts ===")
    counts = list(seq_roots.values())
    counts.sort()
    import statistics
    print(f"  distinct sequence roots: {len(seq_roots)}")
    print(f"  files per seq: min={min(counts)} median={int(statistics.median(counts))} "
          f"mean={statistics.mean(counts):.1f} max={max(counts)}")

    # sample one full sequence to see its file set
    sample_root = next(iter(seq_roots.keys()))
    print(f"\n=== sample sequence file set: {sample_root} ===")
    for p in sorted(RECON.glob(f"{sample_root}*")):
        print(f"  {p.name}  ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
