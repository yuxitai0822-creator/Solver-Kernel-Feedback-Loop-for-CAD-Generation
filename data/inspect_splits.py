"""Inspect train_test.json splits and basic reconstruction structure.

This is part of the pre-experiment data check. It reports:
- the splits defined in train_test.json and their sizes
- the unique sequence ids referenced in the splits
- how many of those sequences actually have files present in reconstruction/
"""
import json
from pathlib import Path

DATASET_ROOT = Path(r"D:\dataset\r1.0.1")
TRAIN_TEST = DATASET_ROOT / "train_test.json"
RECON = DATASET_ROOT / "reconstruction"


def main():
    raw = json.loads(TRAIN_TEST.read_text(encoding="utf-8"))
    print("=== train_test.json keys ===")
    for k, v in raw.items():
        print(f"  {k}: {len(v)}")

    all_seqs = set()
    for k, v in raw.items():
        for sid in v:
            all_seqs.add(sid)
    print(f"\n=== total unique sequence ids referenced ===\n  {len(all_seqs)}")

    # What sequence-id prefixes (design id) exist?
    design_ids = set(sid.rsplit("_", 2)[0] for sid in all_seqs)
    print(f"  unique design ids: {len(design_ids)}")

    # Re-derive sequence-id by grouping files in reconstruction/ by their
    # <designid>_<hash>_<seq> prefix (everything up to the optional extra index).
    print("\n=== checking which referenced sequences have files on disk ===")
    if RECON.exists():
        on_disk = {p.stem for p in RECON.iterdir() if p.is_file()}
        print(f"  total distinct file stems on disk: {len(on_disk)}")
        # Referenced sequence id formats like 133248_c7255340_0000.
        # Files on disk may be 133248_c7255340_0000.* or
        # 133248_c7255340_0000_0001.* (operation sub-states).
        covered = sum(1 for sid in all_seqs if any(s.startswith(sid) for s in on_disk))
        print(f"  referenced seqs with at least one matching file: {covered}/{len(all_seqs)}")
    else:
        print("  reconstruction/ not found")


if __name__ == "__main__":
    main()
