"""p2b_iter_runner.py — M0-M3 iterative agentic system runner.

Walks the same 167 (sid, nid) pairs as the v0 ``p2b_full.py`` does
(138 TypeA + 29 EX2), but for each (method, sid, nid) invokes
``trial_iteration.run()`` instead of a single-shot LLM call.

This is the M0-M3 iter loop framework.  It mirrors the v0 runner's
defensive mechanisms (atomic write, BaseException guard, graceful
KeyboardInterrupt) and writes to a separate output directory
(``experiments/phase2b_iter/``) so the v0 pilot_results.json is
untouched.

Output schema (per trial):

    {
        "method":       "M0_NoFeedback" | "M1_SolverOnly"
                       | "M2_KQPOnly" | "M3_SolverKQP",
        "sid":          "<sid>",
        "nid":          "neg_01" | ...,
        "layer":        "TypeA" | "EX2",
        "iterations":   [ {iter, reasoning, script, verifications}, ... ],
        "final_status": "success" | "failure" | "max_iter_exceeded"
                       | "no_change" | "no_script" | "llm_error",
        "n_iterations": int,
        "feedback_channels_exposed": ["pipeline"] | ["pipeline","solver"] | ...,
        "perturbation_summary": "<one-line>",
        "history_path": "<path or null>",
        "kqp_path":     "<path or null>",
        "wallclock":    float,
    }

The runner is **framework-only** as of the initial commit.  It
imports cleanly and can be smoke-tested on a small sample set; the
user will invoke the actual benchmark when ready.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import method_policy  # noqa: E402
import trial_iteration  # noqa: E402

OUT_DIR = _REPO_ROOT / "experiments" / "phase2b_iter"
RESULTS_PATH = OUT_DIR / "pilot_results.json"


# ---------------------------------------------------------------------------
# Sample discovery (mirrors p2b_full.py — keep in sync)
# ---------------------------------------------------------------------------
def discover_samples():
    """Return (all_type_a, all_ex2) — both are lists of (sid, nid, op)."""
    all_type_a: list[tuple[str, str, str]] = []
    all_ex2:    list[tuple[str, str, str]] = []
    perturb_root = _REPO_ROOT / "task5_negative_perturbation" / "perturbations"
    for sid_dir in perturb_root.iterdir():
        sid = sid_dir.name
        for nid_dir in sid_dir.iterdir():
            nid = nid_dir.name
            meta_p = nid_dir / "perturbation_meta.json"
            if not meta_p.exists():
                continue
            try:
                meta = json.loads(meta_p.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            op = meta.get("operator_input_name") or meta.get("operator") or "?"
            if op.startswith("E") and not op.startswith("EX"):
                all_type_a.append((sid, nid, op))
            elif op == "EX2_coordinate_flip":
                all_ex2.append((sid, nid, op))
    return all_type_a, all_ex2


# ---------------------------------------------------------------------------
# Persistence (atomic write, same defence as p2b_full.py)
# ---------------------------------------------------------------------------
def _save_results(all_results: list[dict]) -> None:
    """Atomically write ``pilot_results.json`` — write to .tmp then
    ``os.replace`` so a power loss / Ctrl+C can lose at most one
    trial, never corrupt the file."""
    tmp_path = RESULTS_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    os.replace(tmp_path, RESULTS_PATH)


def _load_existing_results() -> tuple[list[dict], set[tuple[str, str, str]]]:
    """Resume from an existing run.  Only entries without an
    ``error`` key are added to ``existing_keys`` so transient
    failures are retried."""
    all_results: list[dict] = []
    existing_keys: set[tuple[str, str, str]] = set()
    if RESULTS_PATH.exists():
        try:
            for r in json.loads(RESULTS_PATH.read_text(encoding="utf-8")):
                all_results.append(r)
                if "error" not in r:
                    existing_keys.add((r.get("method"), r.get("sid"), r.get("nid")))
        except Exception:  # noqa: BLE001
            pass
    n_errored = sum(1 for r in all_results if "error" in r)
    print(f"Already done (non-error): {len(existing_keys)}  "
          f"({n_errored} errored will be retried)")
    return all_results, existing_keys


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(only_methods: list[str] | None = None,
         max_samples: int | None = None) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_type_a, all_ex2 = discover_samples()
    print(f"Total samples: TypeA={len(all_type_a)}, EX2={len(all_ex2)}")
    print(f"Total trials × 4 methods: {(len(all_type_a) + len(all_ex2)) * 4}")

    methods = method_policy.METHODS_IN_ORDER
    if only_methods:
        methods = tuple(m for m in methods if m in only_methods)
        if not methods:
            print(f"!! no valid methods in {only_methods}; known: {method_policy.METHODS_IN_ORDER}")
            return

    trials = ([(s, n, o, "TypeA") for s, n, o in all_type_a]
              + [(s, n, o, "EX2")   for s, n, o in all_ex2])
    if max_samples is not None:
        trials = trials[:max_samples]
        print(f"!! smoke-test cap: only running first {max_samples} (sid, nid) pairs")

    print(f"Trials to run: {len(trials)} × {len(methods)} methods = "
          f"{len(trials) * len(methods)}")

    all_results, existing_keys = _load_existing_results()
    n_done = 0
    t_start = time.time()

    try:
        for sid, nid, op, layer in trials:
            for method in methods:
                if (method, sid, nid) in existing_keys:
                    continue
                out_dir = OUT_DIR / method / sid / nid
                out_dir.mkdir(parents=True, exist_ok=True)
                t0 = time.time()
                try:
                    r = trial_iteration.run(
                        method=method,
                        sid=sid,
                        nid=nid,
                        layer=layer,
                        out_dir=out_dir,
                    )
                    r["operator"] = op
                except KeyboardInterrupt:
                    raise
                except BaseException as e:  # noqa: BLE001
                    # Anything else — record and keep going.
                    r = {
                        "method": method,
                        "sid": sid,
                        "nid": nid,
                        "layer": layer,
                        "operator": op,
                        "iterations": [],
                        "final_status": "runner_crash",
                        "n_iterations": 0,
                        "error": f"runner_crash: {type(e).__name__}: {str(e)[:200]}",
                        "trace": traceback.format_exc(limit=4),
                        "wallclock": round(time.time() - t0, 2),
                    }
                if "wallclock" not in r:
                    r["wallclock"] = round(time.time() - t0, 2)
                all_results.append(r)
                n_done += 1
                _save_results(all_results)
                elapsed = round(time.time() - t_start, 1)
                final = r.get("final_status", "?")
                n_iter = r.get("n_iterations", 0)
                chans = "/".join(r.get("feedback_channels_exposed", []))
                err = r.get("error", "-")
                print(f"  [{n_done:3d}] {method:18s} {layer:5s} {sid}/{nid} "
                      f"({op}): status={final} n_iter={n_iter} "
                      f"ch={chans} err={err[:60]} "
                      f"({r['wallclock']}s) [cumul {elapsed}s]", flush=True)
    except KeyboardInterrupt:
        # Persist everything we have so far.
        try:
            _save_results(all_results)
        except Exception:  # noqa: BLE001
            pass
        print(f"\n*** KeyboardInterrupt ***  Persisted {len(all_results)} trials.  "
              f"Re-run to resume.")
        return

    print(f"\nDone. {len(all_results)} trials total.")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="M0-M3 iter benchmark runner.")
    p.add_argument("--methods", nargs="*", default=None,
                    help="Subset of M0_NoFeedback M1_SolverOnly M2_KQPOnly M3_SolverKQP")
    p.add_argument("--max-samples", type=int, default=None,
                    help="Cap on the number of (sid, nid) pairs (for smoke tests).")
    args = p.parse_args()
    main(only_methods=args.methods, max_samples=args.max_samples)
