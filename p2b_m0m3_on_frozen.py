"""p2b_m0m3_on_frozen.py — M0-M3 perturbation repair experiment runner.

Walks every (sid, nid) pair in the **frozen** triple manifest
(``experiments/phase2b_triplets/_frozen_manifest.json``) and runs
the M0-M3 iter loop with ``initial_script = code_perturbed.py``.

The frozen triple's verification result is the *input* contract:
- ``code_gt.py``                — what the LLM should ideally produce
                                  back (or close to).
- ``code_perturbed.py``         — what the LLM starts from, with
                                  T_ref-listed KQP queries that will
                                  now fail.
- ``triplet.json``              — frozen verification record.

The runner reads ``code_perturbed.py``, calls
``trial_iteration.run(initial_script=...)`` for each of the four
methods, and persists the resulting per-iter per-method records to
``experiments/phase2b_m0m3/``.

Output schema (one entry per (method, sid, nid)):

    {
        "method":       "M0_NoFeedback" | "M1_SolverOnly"
                       | "M2_KQPOnly" | "M3_SolverKQP",
        "sid":          "<sid>",
        "nid":          "neg_01" | ...,
        "layer":        "TypeA",
        "iter_records": [ {iter, script, reasoning,
                           verifications{pipeline,solver,kernel}}, ... ],
        "final_status": "success" | "max_iter_exceeded" | "no_change"
                       | "llm_error" | "runner_crash",
        "n_iterations": int,
        "feedback_channels_exposed": ["pipeline", ...],
        "perturbation_summary":     "<one-line T_ref summary>",
        "history_path":             "<Fusion360 history path or null>",
        "kqp_path":                 "<KQP instance path or null>",
        "wallclock":                <seconds>,
        "frozen_input": {
            "code_gt_path":         ...,
            "code_perturbed_path":  ...,
            "step_gt_path":         ...,
            "step_perturbed_path":  ...,
            "triplet_json_path":    ...,
        }
    }

Defensive mechanisms (atom-write + resume + base-exception guard)
mirror ``p2b_iter_runner.py`` so re-runs pick up where they left off.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _bypass_dead_proxy() -> None:
    """If the shell's HTTP/HTTPS_PROXY points at a proxy that
    refuses connections, drop it for this Python process so
    outbound HTTPS goes direct.  Idempotent.  Probes the proxy
    with a 1-second connect attempt."""
    proxies = [k for k in os.environ
              if k.lower() in ("http_proxy", "https_proxy", "all_proxy")]
    if not proxies:
        return
    import socket
    bad = []
    for k in proxies:
        url = os.environ.get(k, "")
        if not url:
            continue
        try:
            host_port = url.split("//", 1)[-1].split("/", 1)[0]
            host, _, port = host_port.partition(":")
            port = int(port or 8080)
            with socket.create_connection((host, port), timeout=1):
                continue  # this proxy is reachable — keep it
        except Exception:  # noqa: BLE001
            bad.append(k)
    if not bad:
        return
    print(f"[defensive] dropping dead proxies: {bad}", flush=True)
    for k in bad:
        os.environ.pop(k, None)
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"


_bypass_dead_proxy()


import method_policy  # noqa: E402
import trial_iteration  # noqa: E402

FROZEN_DIR        = _REPO_ROOT / "experiments" / "phase2b_triplets"
FROZEN_MANIFEST   = FROZEN_DIR / "_frozen_manifest.json"
OUT_ROOT          = _REPO_ROOT / "experiments" / "phase2b_m0m3"
RESULTS_PATH      = OUT_ROOT / "pilot_results.json"


def _load_frozen_pairs() -> list[tuple[str, str]]:
    """Return the (sid, nid) pairs listed in the frozen manifest."""
    m = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []
    for op_block in m["by_operator"].values():
        for s in op_block["samples"]:
            out.append((s["sid"], s["nid"]))
    return out


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _atomic_write(path: Path, payload: list[dict]) -> None:
    """Write ``payload`` to ``path`` via tmp + replace."""
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False,
                                default=str),
                   encoding="utf-8")
    os.replace(tmp, path)


def _load_existing() -> tuple[list[dict], set[tuple[str, str, str]]]:
    """Resume from ``RESULTS_PATH``: keep all entries (for the
    audit log) but only mark a trial as done if its
    ``final_status`` is a clean terminal state.

    Clean states: ``success``, ``max_iter_exceeded``, ``no_change``,
    ``no_script``.  Transient failure states (``llm_error``,
    ``runner_crash``, anything in ``error``) are retried.
    """
    results: list[dict] = []
    done: set[tuple[str, str, str]] = set()
    if RESULTS_PATH.exists():
        try:
            for r in json.loads(RESULTS_PATH.read_text(encoding="utf-8")):
                results.append(r)
                if "error" in r:
                    continue
                if r.get("final_status") not in ("success", "max_iter_exceeded",
                                                 "no_change", "no_script"):
                    continue
                done.add((r["method"], r["sid"], r["nid"]))
        except Exception:  # noqa: BLE001
            pass
    return results, done


def main(methods: list[str] | None = None,
         max_pairs: int | None = None,
         only_sid: list[str] | None = None) -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    pairs = _load_frozen_pairs()
    if only_sid:
        pairs = [(s, n) for (s, n) in pairs if s in only_sid]
    if max_pairs is not None:
        pairs = pairs[:max_pairs]
    print(f"Frozen pairs: {len(pairs)} (after filters)")

    method_order = method_policy.METHODS_IN_ORDER
    if methods:
        method_order = tuple(m for m in method_order if m in methods)
    if not method_order:
        print("!! no methods; abort")
        return
    n_trials = len(pairs) * len(method_order)
    print(f"Trials to run: {len(pairs)} × {len(method_order)} methods = {n_trials}")

    all_results, existing_done = _load_existing()
    n_done = 0
    t_start = time.time()

    try:
        for sid, nid in pairs:
            triplet_dir = FROZEN_DIR / f"{sid}__{nid}"
            perturbed_path = triplet_dir / "code_perturbed.py"
            if not perturbed_path.exists():
                print(f"  SKIP {sid}/{nid}: code_perturbed.py missing")
                continue
            code_perturbed = _read(perturbed_path)

            for method in method_order:
                if (method, sid, nid) in existing_done:
                    continue
                out_dir = OUT_ROOT / method / sid / nid
                out_dir.mkdir(parents=True, exist_ok=True)
                # Persist the input contract alongside the trial.
                (out_dir / "code_perturbed_input.py").write_text(
                    code_perturbed, encoding="utf-8")
                t0 = time.time()
                try:
                    r = trial_iteration.run(
                        method=method,
                        sid=sid,
                        nid=nid,
                        layer="TypeA",
                        out_dir=out_dir,
                        initial_script=code_perturbed,
                    )
                    r["frozen_input"] = {
                        "code_gt_path":         str(triplet_dir / "code_gt.py"),
                        "code_perturbed_path":  str(triplet_dir / "code_perturbed.py"),
                        "triplet_json_path":    str(triplet_dir / "triplet.json"),
                    }
                    r["operator"] = (
                        json.loads((triplet_dir / "triplet.json").read_text(encoding="utf-8"))
                        ["T_ref"].get("operator_input_name")
                        or json.loads((triplet_dir / "triplet.json").read_text(encoding="utf-8"))
                        ["T_ref"].get("operator", "?"))
                except KeyboardInterrupt:
                    raise
                except BaseException as e:  # noqa: BLE001
                    r = {
                        "method": method, "sid": sid, "nid": nid,
                        "layer": "TypeA",
                        "iter_records": [],
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
                _atomic_write(RESULTS_PATH, all_results)
                elapsed = round(time.time() - t_start, 1)
                final = r.get("final_status", "?")
                n_iter = r.get("n_iterations", 0)
                chans = "/".join(r.get("feedback_channels_exposed", []))
                err = r.get("error", "-")
                op = r.get("operator", "?")
                print(f"  [{n_done:3d}/{n_trials}] {method:18s} "
                      f"{sid}/{nid}  op={op[:20]:20s}  status={final:18s} "
                      f"n_iter={n_iter}  ch={chans}  "
                      f"({r['wallclock']}s) [cumul {elapsed}s] "
                      f"err={err[:50]}",
                      flush=True)
    except KeyboardInterrupt:
        try:
            _atomic_write(RESULTS_PATH, all_results)
        except Exception:  # noqa: BLE001
            pass
        print(f"\n*** KeyboardInterrupt ***  Persisted {len(all_results)} trials.")
        return

    print(f"\nDone. {len(all_results)} trials total.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--methods", nargs="*", default=None,
                   help="Subset of M0/M1/M2/M3 (default: all four).")
    p.add_argument("--max-pairs", type=int, default=None,
                   help="Cap on the number of (sid, nid) pairs (for smoke tests).")
    p.add_argument("--only-sid", nargs="*", default=None,
                   help="Restrict to specific sids.")
    args = p.parse_args()
    main(methods=args.methods, max_pairs=args.max_pairs,
         only_sid=args.only_sid)
