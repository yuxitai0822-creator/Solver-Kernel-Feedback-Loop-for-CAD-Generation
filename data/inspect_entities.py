"""Inspect the 'entities' dict and 'sequence' more deeply.

We need to find:
- what entity types exist (Sketch, Extrude, Profile, ...)
- whether SKETCH CONSTRAINTS (geometric/dimensional) are encoded anywhere —
  this is the make-or-break for the Constraint Solver feedback arm
- the structure of a sketch entity and an extrude entity
"""
import json
from collections import Counter
from pathlib import Path

SAMPLE = Path(r"D:\dataset\r1.0.1\reconstruction\100106_7f144e5b_0000.json")


def main():
    d = json.loads(SAMPLE.read_text(encoding="utf-8"))
    ents = d["entities"]
    seq = d["sequence"]

    # classify entities by their 'type' field if present, else by structure keys
    type_counter = Counter()
    ent_examples = {}
    for uuid, e in ents.items():
        # entity type often stored as 'type' or inferrable from keys
        etype = e.get("type") if isinstance(e, dict) else None
        if etype is None and isinstance(e, dict):
            # try common keys
            for cand in ("type", "entity_type", "kind"):
                if cand in e:
                    etype = e[cand]
                    break
        if etype is None:
            etype = "<keys:" + ",".join(sorted(list(e.keys())[:4])) + ">" if isinstance(e, dict) else "?"
        type_counter[etype] += 1
        if etype not in ent_examples:
            ent_examples[etype] = e
    print("=== entity 'type' distribution ===")
    for t, c in type_counter.most_common():
        print(f"  {t}: {c}")

    print("\n=== full entity examples (one per type) ===")
    for t, e in ent_examples.items():
        print(f"\n--- type={t} ---")
        s = json.dumps(e, indent=2)
        print(s[:2500])

    # sequence 'type' distribution
    print("\n\n=== sequence 'type' distribution ===")
    stypes = Counter(s.get("type") for s in seq)
    for t, c in stypes.most_common():
        print(f"  {t}: {c}")

    # look for any key resembling 'constraint' across the whole doc
    print("\n=== searching for constraint-related keys across JSON ===")
    found = set()

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                kl = k.lower()
                if "constrain" in kl or "dimens" in kl or "coincident" in kl or "parallel" in kl or "perpend" in kl or "horizont" in kl or "vertical" in kl or "fix" == kl or "symmetric" in kl:
                    found.add(path + "/" + k)
                walk(v, path + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + f"[{i}]")
    walk(d)
    for f in sorted(found):
        print("  ", f)
    if not found:
        print("  (none found)")


if __name__ == "__main__":
    main()
