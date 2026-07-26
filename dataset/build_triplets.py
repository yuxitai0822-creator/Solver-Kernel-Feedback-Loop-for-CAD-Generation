"""dataset/build_triplets.py — CLI entry point for the triplet dataset.

Walks every ``task5_negative_perturbation/perturbations/<sid>/<nid>/``
directory that has both a ``perturbed_history.json`` and a
``perturbation_meta.json``, calls ``dataset.triplet.build_triplet``
on each pair, and writes a per-pair ``triplet.json`` under
``experiments/phase2b_triplets/<sid>__<nid>/``.

Sample discovery is identical to the one used by ``p2b_full.py`` and
``p2b_iter_runner.py``: an ``operator`` field on the
``perturbation_meta.json`` decides whether the sample is a TypeA
parameter-perturbation (``E*``) or an EX2 axis-flip perturbation
(``EX2_coordinate_flip``).

EX1 / EX2 perturbations where ``perturbed_history.json`` is absent
are skipped silently (the user spec notes that the negative-CAD-code
modality isn't always built for those).

Usage
-----

::

    python dataset/build_triplets.py                 # build all
    python dataset/build_triplets.py --max-samples 3  # smoke test

The runner writes an aggregated ``_manifest.json`` at the end of the
run so the analysis layer can find every verified triplet.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import method_policy  # noqa: E402  (m0-m3 policy — may be reused later)
from dataset.triplet import build_triplet, save_triplet  # noqa: E402

PERTURBATIONS_ROOT = _REPO_ROOT / "task5_negative_perturbation" / "perturbations"
DEFAULT_OUT_ROOT = _REPO_ROOT / "experiments" / "phase2b_triplets"
MANIFEST_PATH = DEFAULT_OUT_ROOT / "_manifest.json"


def discover_pairs():
    """Return ``[(sid, nid, op, layer)]`` for every perturbation that
    has both ``perturbed_history.json`` and ``perturbation_meta.json``
    on disk."""
    pairs: list[tuple[str, str, str, str]] = []
    if not PERTURBATIONS_ROOT.exists():
        return pairs
    for sid_dir in sorted(PERTURBATIONS_ROOT.iterdir()):
        if not sid_dir.is_dir():
            continue
        sid = sid_dir.name
        for nid_dir in sorted(sid_dir.iterdir()):
            if not nid_dir.is_dir():
                continue
            nid = nid_dir.name
            meta_p = nid_dir / "perturbation_meta.json"
            if not meta_p.exists():
                continue
            try:
                meta = json.loads(meta_p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not (nid_dir / "perturbed_history.json").exists():
                continue
            op = meta.get("operator_input_name") or meta.get("operator") or "?"
            layer = "EX2" if (op == "EX2_coordinate_flip"
                              or nid.startswith("ex")) else "TypeA"
            pairs.append((sid, nid, op, layer))
    return pairs


def main(max_samples: int | None = None,
         only_sid: list[str] | None = None,
         out_root: Path = DEFAULT_OUT_ROOT,
         timeout: int = 120) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    pairs = discover_pairs()
    print(f"Discovered {len(pairs)} perturbation pairs.")
    if only_sid:
        pairs = [(s, n, o, l) for (s, n, o, l) in pairs if s in only_sid]
        print(f"After --only-sid filter: {len(pairs)}.")
    if max_samples is not None:
        pairs = pairs[:max_samples]
        print(f"After --max-samples cap: {len(pairs)}.")

    # Resume: skip any (sid, nid) that already has a verified
    # triplet.json on disk.
    todo: list[tuple[str, str, str, str]] = []
    skipped_resumed = 0
    for (sid, nid, op, layer) in pairs:
        triplet_json = out_root / f"{sid}__{nid}" / "triplet.json"
        if triplet_json.exists():
            skipped_resumed += 1
            continue
        todo.append((sid, nid, op, layer))
    print(f"Already done (resume): {skipped_resumed}; to run: {len(todo)}.")

    # Aggregate stats.
    verified = 0
    layer_fail_counts: Counter = Counter()
    layer_pass_counts: Counter = Counter()

    # Trial-level log (atomic write every trial).
    runs_log = out_root / "_runs.json"

    runs: list[dict] = []
    if runs_log.exists():
        try:
            runs = json.loads(runs_log.read_text(encoding="utf-8"))
        except Exception:
            runs = []

    t_start = time.time()
    n_done = 0
    for (sid, nid, op, layer) in todo:
        n_done += 1
        t0 = time.time()
        try:
            triplet = build_triplet(sid, nid, out_root=out_root, timeout=timeout)
        except KeyboardInterrupt:
            raise
        except BaseException as e:  # noqa: BLE001
            print(f"  [{n_done}/{len(todo)}] {sid}/{nid}: runner_crash "
                  f"{type(e).__name__}: {str(e)[:200]}", flush=True)
            runs.append({"sid": sid, "nid": nid, "op": op, "layer": layer,
                         "runner_crash": f"{type(e).__name__}: {str(e)[:200]}",
                         "trace": traceback.format_exc(limit=4),
                         "wallclock": round(time.time() - t0, 2)})
            tmp = runs_log.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(runs, indent=2, default=str), encoding="utf-8")
            os.replace(tmp, runs_log)
            continue

        save_triplet(triplet)
        d = triplet.to_dict()
        runs.append({"sid": sid, "nid": nid, "op": op, "layer": layer,
                     "verified": triplet.verified,
                     "wallclock": triplet.wallclock,
                     "l1": triplet.layer1_pipeline_perturbed.get("compile_status"),
                     "l2": [c["status"] for c in triplet.layer2_fidelity["checks"]],
                     "l3_actual": triplet.layer3_difference.get("actual_failed"),
                     "l3_expected": triplet.layer3_difference.get("expected_failed"),
                     "l3_missing": triplet.layer3_difference.get("missing_expected"),
                     "l3_extras":   triplet.layer3_difference.get("extras"),
                     "note": triplet.notes})
        # Atomic write.
        tmp = runs_log.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(runs, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, runs_log)

        # Status tally.
        if triplet.verified:
            verified += 1
            layer_pass_counts[layer] += 1
        else:
            layer_fail_counts[layer] += 1

        print(f"  [{n_done}/{len(todo)}] {sid}/{nid}  op={op[:24]:24s} "
              f"layer={layer:5s}  -> verified={triplet.verified} "
              f"({triplet.wallclock}s) "
              f"L2={[c['status'] for c in triplet.layer2_fidelity['checks']]} "
              f"L3actual={triplet.layer3_difference.get('actual_failed')} "
              f"L3missing={triplet.layer3_difference.get('missing_expected')} "
              f"L3extras={triplet.layer3_difference.get('extras')}",
              flush=True)

    # Manifest summary.
    manifest = {
        "n_pairs":            len(pairs),
        "n_already_resumed":  skipped_resumed,
        "n_run":              n_done,
        "n_verified":         verified,
        "n_failed":           n_done - verified,
        "pass_per_layer":     dict(layer_pass_counts),
        "fail_per_layer":     dict(layer_fail_counts),
        "wallclock_total":    round(time.time() - t_start, 2),
        "out_root":           str(out_root),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2),
                              encoding="utf-8")
    print()
    print("=" * 60)
    print(f"Done. {n_done} trials; verified={verified}; "
          f"failed={n_done - verified}.")
    print(f"Pass per layer: {dict(layer_pass_counts)}  "
          f"Fail per layer: {dict(layer_fail_counts)}")
    print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Triplet dataset builder for M0-M3 perturbation experiment.")
    p.add_argument("--max-samples", type=int, default=None,
                   help="Cap on the number of perturbations to process.")
    p.add_argument("--only-sid", nargs="*", default=None,
                   help="Restrict to specific sids (repeatable).")
    p.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    p.add_argument("--timeout", type=int, default=120)
    args = p.parse_args()
    main(max_samples=args.max_samples,
         only_sid=args.only_sid,
         out_root=args.out_root,
         timeout=args.timeout)
