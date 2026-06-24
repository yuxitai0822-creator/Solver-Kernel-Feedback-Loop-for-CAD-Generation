"""Deep-inspect the structure of a reconstruction *.json design sequence.

The JSON is the source from which the experiment's JSON Design Plan must be
*deterministically* extracted. We need to understand: metadata, timeline,
entities, properties, sequence — and crucially where constraints live,
because the Constraint Solver feedback depends on them.
"""
import json
from pathlib import Path

SAMPLE = Path(r"D:\dataset\r1.0.1\reconstruction\100106_7f144e5b_0000.json")


def show(label, obj, indent=0):
    pad = "  " * indent
    if isinstance(obj, dict):
        print(f"{pad}{label}: dict({len(obj)} keys) -> {list(obj.keys())}")
    elif isinstance(obj, list):
        print(f"{pad}{label}: list[{len(obj)}]")
        if obj:
            print(f"{pad}  [0] type={type(obj[0]).__name__}")
            show("[0]", obj[0], indent + 1)
    else:
        s = repr(obj)
        if len(s) > 120:
            s = s[:120] + "..."
        print(f"{pad}{label}: {type(obj).__name__} = {s}")


def main():
    d = json.loads(SAMPLE.read_text(encoding="utf-8"))
    print("=== TOP LEVEL ===")
    for k, v in d.items():
        show(k, v, 1)

    print("\n=== metadata (full) ===")
    print(json.dumps(d.get("metadata"), indent=2)[:2000])

    # entities is the heart of the construction script — dig into types
    ents = d.get("entities")
    if isinstance(ents, list) and ents:
        print("\n=== entity type distribution (this sample) ===")
        from collections import Counter
        etypes = Counter()
        for e in ents:
            if isinstance(e, dict):
                etypes[e.get("type", "?")] += 1
        for t, c in etypes.most_common():
            print(f"  {t}: {c}")
        print("\n=== first 3 entities (full) ===")
        for e in ents[:3]:
            print(json.dumps(e, indent=2)[:1500])
            print("  ----")

    # timeline
    tl = d.get("timeline")
    if isinstance(tl, list) and tl:
        print("\n=== timeline[0] (full) ===")
        print(json.dumps(tl[0], indent=2)[:1500])

    # sequence
    seq = d.get("sequence")
    if isinstance(seq, dict):
        print("\n=== sequence keys ===", list(seq.keys()))
    elif isinstance(seq, list):
        print("\n=== sequence[0] (full) ===")
        print(json.dumps(seq[0], indent=2)[:1500])


if __name__ == "__main__":
    main()
