"""dataset/freeze_verified.py — mark the 120 verified triplets as frozen.

Reads ``experiments/phase2b_triplets/<sid>__<nid>/triplet.json``,
adds a top-level ``"frozen": true`` field (for at-a-glance status
when reading the file), and writes an aggregate
``_frozen_manifest.json`` listing the (sid, nid) pairs by operator
class.

The frozen set is the **input** for the M0-M3 perturbation
experiment — for each ``(sid, nid)`` and each method ``M0..M3`` the
runner will feed ``code_perturbed.py`` into the iter loop as the
starting script.

Idempotent: running this twice is fine; the second run simply
overwrites the same fields.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

OUT_DIR = _REPO_ROOT / "experiments" / "phase2b_triplets"
MANIFEST_PATH = OUT_DIR / "_frozen_manifest.json"


def main() -> None:
    triples: list[tuple[str, str, str]] = []
    for p in sorted(OUT_DIR.glob("*/triplet.json")):
        text = p.read_text(encoding="utf-8")
        t = json.loads(text)
        if not t.get("verified"):
            continue
        t["frozen"] = True
        t["frozen_at"] = t.get("frozen_at") or "2026-07-24"
        p.write_text(json.dumps(t, indent=2, ensure_ascii=False,
                                default=str),
                      encoding="utf-8")
        sid = t["sid"]
        nid = t["nid"]
        op = (t["T_ref"].get("operator_input_name")
              or t["T_ref"].get("operator"))
        triples.append((sid, nid, op))

    # Group by operator for the manifest view.
    by_op: dict[str, list[dict[str, str]]] = {}
    for sid, nid, op in triples:
        by_op.setdefault(op, []).append({"sid": sid, "nid": nid})

    manifest = {
        "freeze_date": "2026-07-24",
        "n_triples": len(triples),
        "by_operator": {op: {"count": len(items), "samples": items}
                          for op, items in sorted(by_op.items())},
        "note": ("These 120 (sid, nid) pairs have passed L1 + L2 + L3 "
                 "in `triplet.json`.  They are the input dataset for the "
                 "M0-M3 perturbation repair experiment."),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2,
                                         ensure_ascii=False),
                              encoding="utf-8")
    print(f"Froze {len(triples)} verified triplets.")
    print(f"Per operator: {[(op, len(items)) for op, items in by_op.items()]}")
    print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
