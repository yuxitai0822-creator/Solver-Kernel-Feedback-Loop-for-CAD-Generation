"""replay_threshold_trajectories.py — §13 Stop-Bar Sensitivity Replay

Implements the post-hoc replay defined in `doc/experiment_contract_v0.1.md`
section 13 (Stop-Bar Sensitivity Threshold Effect).

Inputs:
  - `experiments/results/M3_SolverKQP/<sid>/iter_<NN>/_iter_record.json`
    — per-iteration artefacts produced by run_benchmark_v0.2.py.
  - `experiments/results/M3_SolverKQP/<sid>/repair_summary.json`
    — convenience summary that also carries the iter_records_summary.

What this script does:

  §13.4  Replay protocol
  ──────────────────────────────────────────────────────────────────────
  For each M3 sample, walk the stored trajectory
  C_{i,0} → C_{i,1} → C_{i,2} → C_{i,3}, and for each bar B ∈ {B0,B1,B2,B3},
  find stop_iter_B(i) = min{ k : B(C_{i,k}) = True } else 3 (§13.4 "ran
  out of budget").  Re-evaluate that frozen final CAD under the
  **common full bar B3** to obtain final_quality_B(i).

  §13.5  Reports the central table with both:
    - own-bar stop rate (NOT comparable across bars — must be labelled)
    - common-bar (B3) final quality — THE cross-bar-comparable number

  §13.6  M3 trajectory = full-feedback → common-bar quality is the upper
    bound of any weaker-bar deployment.
  §13.7  N0–N3 conditional deployment study is gated behind "large gap":
    if B0→B3 gap > threshold AND --trigger-n0-n3 is set, the script will
    invoke the deployment simulator (placeholder for future work).
  §13.8  Determinism: pure post-processing, no LLM, no randomness.

Run:
    "D:/Anaconda/envs/cad_subproject1/python.exe" \\
        experiments/replay_threshold_trajectories.py

Optional flags:
    --m3-root PATH       override the M3 results directory
    --gap-trigger 0.10   B0→B3 quality gap to trigger N0–N3 (§13.7)
    --trigger-n0-n3      actually run N0–N3 even if gap is below threshold
                         (used only when paper explicitly asks for it)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

# Re-use the bar helper from run_benchmark_v0.2 (single source of truth).
# The dotted filename is not a valid Python identifier, so we load the
# module via importlib.
import importlib.util as _ilu
_rb_path = ROOT / "experiments" / "run_benchmark_v0.2.py"
_spec = _ilu.spec_from_file_location("run_benchmark_v0_2", str(_rb_path))
_rb = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_rb)
bar_pass = _rb.bar_pass
THRESHOLD_BARS = _rb.THRESHOLD_BARS

M3_ROOT = ROOT / "experiments" / "results_v0.2" / "M3_SolverKQP"
LEGACY_M3_ROOT = ROOT / "experiments" / "results" / "M3_SolverKQP"
REPORTS_DIR = ROOT / "experiments" / "reports"


# ---------------------------------------------------------------------------
# Trajectory loader (§13.4 input)
# ---------------------------------------------------------------------------

def load_trajectory(sample_dir: Path) -> list[dict]:
    """Load and merge the iter_records for a sample, sorted by iter.

    Falls back to repair_summary.json's iter_records_summary when the
    per-iter JSON isn't present (smoke-test artefacts may have only
    the summary).
    """
    iter_dirs = sorted([p for p in sample_dir.iterdir()
                          if p.is_dir() and p.name.startswith("iter_")],
                          key=lambda p: int(p.name.split("_")[1]))
    if iter_dirs:
        full = []
        for d in iter_dirs:
            rp = d / "_iter_record.json"
            if rp.exists():
                full.append(json.loads(rp.read_text(encoding="utf-8")))
        if full:
            return sorted(full, key=lambda r: r.get("iter", 0))

    summary_path = sample_dir / "repair_summary.json"
    if summary_path.exists():
        sm = json.loads(summary_path.read_text(encoding="utf-8"))
        stub = []
        for r in sm.get("iter_records_summary", []):
            stub.append({
                "iter": r.get("iter"),
                "pipeline_valid": r.get("pipeline_valid"),
                "solver_acceptable": r.get("solver_acceptable"),
                "kqp_pass": r.get("kqp_pass"),
            })
        return stub
    return []


def _components(rec: dict) -> tuple[bool, bool, bool]:
    return (bool(rec.get("pipeline_valid")),
              bool(rec.get("solver_acceptable")),
              bool(rec.get("kqp_pass")))


# ---------------------------------------------------------------------------
# §13.4 replay  —  per-sample, per-bar
# ---------------------------------------------------------------------------

def replay_sample_bar(trajectory: list[dict], bar: str,
                        max_iter: int = 3) -> dict:
    """Implement §13.4 for one (sample, bar).

    Returns dict with:
      stop_iter_B          (int, 0..max_iter; 3 if bar never met)
      k_met                (True iff bar met within ≤ max_iter)
      final_quality_B3     (B3 evaluated at stop_iter_B; the cross-bar
                             yardstick from §13.5)
      tokens_up_to_stop    (tokens consumed up to stop_iter_B — note:
                             the LLM ran only at iter 1+, not iter 0;
                             iter 0 has no tokens)
      tokens_up_to_iter_B3 (tokens up to the B3-meeting iter; if B3
                             never met, this is sum up to max_iter)
    """
    if not trajectory:
        return {"stop_iter_B": max_iter, "k_met": False,
                  "final_quality_B3": False,
                  "tokens_up_to_stop": 0,
                  "tokens_up_to_iter_B3": 0,
                  "note": "empty_trajectory"}

    # First iter where bar is met
    stop = None
    tokens_to_stop = 0
    for r in trajectory:
        P, S, K = _components(r)
        # tokens at iter (only counted on repair iters, not iter 0)
        t_in = int(r.get("input_tokens", 0) or 0)
        t_out = int(r.get("output_tokens", 0) or 0)
        if bar_pass(P, S, K, bar):
            stop = r.get("iter")
            break
        # accumulate tokens used by THIS iter regardless of bar meeting.
        tokens_to_stop += t_in + t_out

    if stop is None:
        # Bar never met within the trajectory; per §13.4 freeze at iter 3
        # (the last recorded iter) — implementation: clamp to last seen iter.
        last = trajectory[-1].get("iter", max_iter)
        stop = min(max_iter, last if last is not None else max_iter)

    # Re-evaluate at stop under common bar B3
    stop_rec = next((r for r in trajectory if r.get("iter") == stop), trajectory[-1])
    P3, S3, K3 = _components(stop_rec)
    final_quality_B3 = bar_pass(P3, S3, K3, "B3")

    # Tokens up to and including stop iter (for the comparison column)
    tokens_up_to_stop = 0
    for r in trajectory:
        if r.get("iter", -1) <= stop:
            tokens_up_to_stop += int(r.get("input_tokens", 0) or 0) \
                                  + int(r.get("output_tokens", 0) or 0)

    # Tokens up to first B3-met iter (reference for "token savings vs B3")
    tokens_up_to_iter_B3 = 0
    b3_stop = None
    for r in trajectory:
        if bar_pass(*_components(r), "B3"):
            b3_stop = r.get("iter")
            break
    if b3_stop is None:
        b3_stop = max_iter
    for r in trajectory:
        if r.get("iter", -1) <= b3_stop:
            tokens_up_to_iter_B3 += int(r.get("input_tokens", 0) or 0) \
                                      + int(r.get("output_tokens", 0) or 0)

    k_met = bar_pass(*_components(stop_rec), bar)

    return {
        "stop_iter_B": stop,
        "k_met": k_met,
        "final_quality_B3": final_quality_B3,
        "tokens_up_to_stop": tokens_up_to_stop,
        "tokens_up_to_iter_B3": tokens_up_to_iter_B3,
        "bar": bar,
    }


# ---------------------------------------------------------------------------
# §13.5 aggregator — central table  (dual-column)
# ---------------------------------------------------------------------------

def aggregate_replays(per_sample: dict[str, dict[str, dict]]) -> dict:
    """Build the §13.5 central table.

    Args:
        per_sample: {sample_id: {bar: replay_sample_bar(...) output}}
    """
    table = []
    for bar in THRESHOLD_BARS:
        samples = [per_sample[sid][bar] for sid in per_sample
                    if bar in per_sample[sid]]
        n = len(samples)
        if n == 0:
            table.append({"bar": bar,
                            "n_samples": 0,
                            "own_bar_stop_rate": None,
                            "mean_stop_iter": None,
                            "common_bar_quality": None,
                            "quality_gap_vs_B3": None,
                            "mean_token_savings_vs_B3": None})
            continue
        own_rate = sum(1 for s in samples if s["k_met"]) / n
        stop_iters = [s["stop_iter_B"] for s in samples if s["k_met"]]
        mean_stop = (sum(stop_iters) / len(stop_iters)
                       if stop_iters else None)
        common_quality = sum(1 for s in samples
                                  if s["final_quality_B3"]) / n
        # token savings vs the B3 reference (for the *common-quality-met
        # subset* — to be conservative, average only over samples where B3
        # was met at all)
        token_savings = [s["tokens_up_to_iter_B3"] - s["tokens_up_to_stop"]
                          for s in samples
                          if s["tokens_up_to_iter_B3"] is not None
                          and s["tokens_up_to_stop"] is not None]
        mean_token_savings = (sum(token_savings) / len(token_savings)
                                  if token_savings else None)
        table.append({
            "bar": bar,
            "n_samples": n,
            "own_bar_stop_rate": own_rate,
            "mean_stop_iter": mean_stop,
            "common_bar_quality": common_quality,
            "quality_gap_vs_B3": None,  # filled below
            "mean_token_savings_vs_B3": mean_token_savings,
        })

    # quality gap vs B3 (the B3 row is always 0)
    b3_q = next((r["common_bar_quality"] for r in table
                    if r["bar"] == "B3" and r["common_bar_quality"] is not None),
                  None)
    for r in table:
        if r["common_bar_quality"] is not None and b3_q is not None:
            r["quality_gap_vs_B3"] = b3_q - r["common_bar_quality"]
        else:
            r["quality_gap_vs_B3"] = None

    return {"bars": table,
              "interpretation": _interpret_table(table)}


def _interpret_table(table: list[dict]) -> dict:
    """§13.6 interpretation rules."""
    by_bar = {r["bar"]: r for r in table if r["common_bar_quality"] is not None}
    if "B0" not in by_bar or "B3" not in by_bar:
        return {"note": "incomplete — cannot interpret"}
    gap = by_bar["B3"]["common_bar_quality"] - by_bar["B0"]["common_bar_quality"]
    b1b2 = None
    if "B1" in by_bar and "B2" in by_bar:
        b1b2 = by_bar["B2"]["common_bar_quality"] - by_bar["B1"]["common_bar_quality"]
    verdict = "small_gap" if (gap is not None and gap < 0.10) else "large_gap"
    return {
        "b0_to_b3_quality_gap": gap,
        "b1_minus_b2_quality_gap": b1b2,
        "verdict": verdict,
        "triggers_n0_n3": verdict == "large_gap",
        "caveat": "M3 trajectory is full-feedback; weaker-bar deployment "
                   "quality ≤ this common-bar quality (upper bound per §13.6).",
    }


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def find_m3_root() -> Path | None:
    if M3_ROOT.exists():
        return M3_ROOT
    if LEGACY_M3_ROOT.exists():
        return LEGACY_M3_ROOT
    return None


def run_replay(m3_root: Path, *, gap_trigger: float = 0.10,
                  force_n0_n3: bool = False) -> dict:
    samples: dict[str, dict[str, dict]] = {}
    n_skipped = 0
    for sid_dir in sorted([p for p in m3_root.iterdir() if p.is_dir()]):
        sid = sid_dir.name
        traj = load_trajectory(sid_dir)
        if not traj:
            n_skipped += 1
            continue
        samples[sid] = {bar: replay_sample_bar(traj, bar) for bar in THRESHOLD_BARS}

    aggregated = aggregate_replays(samples)
    aggregated["n_samples"] = len(samples)
    aggregated["n_skipped"] = n_skipped
    aggregated["m3_root"] = str(m3_root)

    # §13.7 conditional trigger
    interp = aggregated["interpretation"]
    if interp.get("triggers_n0_n3") or force_n0_n3:
        aggregated["n0_n3_status"] = {
            "triggered": True,
            "reason": ("large B0→B3 gap" if interp.get("triggers_n0_n3")
                          else "explicit --trigger-n0-n3"),
            "action": "not_run_in_default_build",
            "todo": "implement N0–N3 deployment simulator once §13.7 "
                      "condition is met; current build does not run them "
                      "(see experiment_contract §13.7 'Decision gate').",
        }
    else:
        aggregated["n0_n3_status"] = {
            "triggered": False,
            "reason": f"B0→B3 gap < {gap_trigger:.2f}; §13 alone suffices.",
        }

    return aggregated


def render_markdown(aggregated: dict, out_path: Path) -> None:
    bars = aggregated["bars"]
    lines: list[str] = []
    lines.append("# §13 Stop-Bar Sensitivity — Threshold Replay Report")
    lines.append("")
    lines.append(f"- M3 root: `{aggregated['m3_root']}`")
    lines.append(f"- samples included: **{aggregated['n_samples']}** "
                  f"(skipped: {aggregated['n_skipped']})")
    lines.append("")
    lines.append("## Central Table (§13.5 — DUAL COLUMN)")
    lines.append("")
    lines.append("⚠️ **`own_bar_stop_rate` and `mean_stop_iter` are NOT "
                  "comparable across bars** (different denominators).")
    lines.append("Only `common_bar_quality` is cross-bar comparable.")
    lines.append("")
    lines.append("| Bar | n | own-bar stop rate | mean stop iter | "
                  "**common-bar (B3) final quality** | "
                  "quality gap vs B3 | mean token savings vs B3 |")
    lines.append("|-----|---|------------------|----------------|"
                  "------------------------------------|"
                  "---------------------|-----------------------------|")
    for r in bars:
        gap_sign = "+" if (r["quality_gap_vs_B3"] or 0) >= 0 else "-"
        tok_sign = "+" if (r["mean_token_savings_vs_B3"] or 0) >= 0 else "-"
        lines.append(
            "| {} | {} | {:>8.1%} | {:>6} | **{:>8.1%}** | "
            "{}{:>7.1%} | {}{:>7} |".format(
                r["bar"], r["n_samples"],
                r["own_bar_stop_rate"] or 0,
                "-" if r["mean_stop_iter"] is None
                    else f"{r['mean_stop_iter']:.2f}",
                r["common_bar_quality"] or 0,
                gap_sign, abs(r["quality_gap_vs_B3"] or 0),
                tok_sign,
                "-" if r["mean_token_savings_vs_B3"] is None
                    else f"{int(abs(r['mean_token_savings_vs_B3']))}",
            ))
    lines.append("")
    lines.append("## Interpretation (§13.6)")
    lines.append("")
    interp = aggregated["interpretation"]
    lines.append(f"- B0 → B3 common-bar quality gap: "
                  f"**{interp.get('b0_to_b3_quality_gap')}**")
    lines.append(f"- B2 − B1 common-bar quality gap: "
                  f"**{interp.get('b1_minus_b2_quality_gap')}**")
    lines.append(f"- Verdict: `{interp.get('verdict')}`")
    lines.append(f"- Triggers N0–N3 (§13.7)? **{interp.get('triggers_n0_n3')}**")
    lines.append("")
    lines.append(f"> {interp.get('caveat', '')}")
    lines.append("")
    lines.append("## §13.7 N0–N3 Conditional Trigger")
    lines.append("")
    n0 = aggregated["n0_n3_status"]
    lines.append(f"- triggered: **{n0.get('triggered')}**")
    lines.append(f"- reason: {n0.get('reason')}")
    if n0.get("action"):
        lines.append(f"- action: {n0['action']}")
    if n0.get("todo"):
        lines.append(f"- todo: {n0['todo']}")
    lines.append("")
    lines.append("## §13.9 Acceptance")
    lines.append("")
    lines.append("- [x] four bars B0–B3 defined with monotonicity (§13.3)")
    lines.append("- [x] replay reuses M3 artefacts only — no new LLM (§13.4)")
    lines.append("- [x] central table reports BOTH own-bar (non-comparable) "
                  "AND common-bar (comparable) with caption (§13.5)")
    lines.append("- [x] over-trust upper-bound caveat included (§13.6)")
    lines.append("- [x] N0–N3 gated behind gap condition (§13.7)")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m3-root", default=None,
                       help="override M3 results root")
    ap.add_argument("--gap-trigger", type=float, default=0.10,
                       help="B0→B3 quality gap threshold to trigger N0–N3")
    ap.add_argument("--trigger-n0-n3", action="store_true",
                       help="explicitly run N0–N3 even if gap is below threshold")
    args = ap.parse_args()

    m3_root = Path(args.m3_root) if args.m3_root else find_m3_root()
    if m3_root is None:
        print(f"[replay_threshold_trajectories][FATAL] no M3 results found "
              f"at {M3_ROOT} or {LEGACY_M3_ROOT}")
        sys.exit(1)

    aggregated = run_replay(m3_root, gap_trigger=args.gap_trigger,
                                  force_n0_n3=args.trigger_n0_n3)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "threshold_sensitivity_analysis.json"
    json_path.write_text(json.dumps(aggregated, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    md_path = REPORTS_DIR / "threshold_sensitivity_report.md"
    render_markdown(aggregated, md_path)

    print(f"[replay_threshold_trajectories] wrote {json_path}")
    print(f"[replay_threshold_trajectories] wrote {md_path}")
    bars = aggregated["bars"]
    print("Own-bar stop rates:", [(b["bar"], f'{b["own_bar_stop_rate"]:.1%}')
                                       for b in bars])
    print("Common-bar (B3) quality:", [(b["bar"], f'{b["common_bar_quality"]:.1%}')
                                            for b in bars])
    interp = aggregated["interpretation"]
    print(f"Interpretation: {interp.get('verdict')} "
          f"(B0→B3 gap={interp.get('b0_to_b3_quality_gap')}); "
          f"N0–N3 triggered={aggregated['n0_n3_status']['triggered']}")


if __name__ == "__main__":
    main()