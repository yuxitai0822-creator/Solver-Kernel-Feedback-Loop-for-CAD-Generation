# §13 Stop-Bar Sensitivity — Freeze Report

> **Date**: 2026-07-16
> **Status**: §13 PROTOCOL FROZEN, AWAITING M3 BATCH TO PRODUCE MEANINGFUL NUMBERS
> **Files**: `experiments/replay_threshold_trajectories.py` ·
>           `experiments/config/benchmark_config_v0.2.json` (`secondary_analysis`)
> **Companion artefacts**: `experiments/reports/threshold_sensitivity_analysis.json`,
>                           `experiments/reports/threshold_sensitivity_report.md`

---

## 1. Scope

Implements `doc/experiment_contract_v0.1.md §13` (Stop-Bar Sensitivity /
Threshold Effect) end-to-end.  §13 answers **RQ-T** (does the strictness
of the stop bar itself affect final CAD quality?), which is
**complementary** to the main M0–M3 ablation:

| Layer | Question | RQ | Trigger | Cost |
|---|---|---|---|---|
| Main ablation M0–M3 | feedback value | RQ1/2/3 | always | 1 × batch |
| §13 replay | stop-bar strictness | RQ-T | always (after M3) | **zero new LLM** |
| §13.7 N0–N3 | deployment over-trust | RQ-D | **conditional** on §13.6 verdict | full batch × 4 |

The 4 layers are designed to be statistically separable: M0–M3 holds
the stop bar fixed and varies the feedback; §13 holds the feedback fixed
(full M3 trajectory) and varies the bar; N0–N3 varies both.

---

## 2. Implementation map

| § | Contract clause | Implementation |
|---|---|---|
| §13.3 | 4 nested bars B0 ⊆ B1 ⊆ B3, B0 ⊆ B2 ⊆ B3 | `bar_pass(P, S, K, bar)` helper in `run_benchmark_v0.2.py` |
| §13.3 | B3 = main ablation's stop criterion | Documented as the identical conjunction |
| §13.4 | post-hoc replay on M3 trajectory | `replay_threshold_trajectories.py::replay_sample_bar` |
| §13.5 | dual-column central table | `aggregate_replays` + `render_markdown` |
| §13.6 | interpretation rules + upper-bound caveat | `_interpret_table` |
| §13.7 | conditional N0–N3 trigger | `_interpret_table.verdict == 'large_gap'`; N0–N3 itself is **not** implemented (per contract "decision gate") |
| §13.8 | deterministic, no LLM | script imports no LLM; uses stored `iter_records` only |
| §13.9 | 5 acceptance items | checklist at end of `threshold_sensitivity_report.md` |
| §11.11 | acceptance gate | added as item 11 |

---

## 3. Components

### 3.1 `bar_pass(P, S, K, bar)` — the single source of truth for §13.3

```python
def bar_pass(pipeline_valid, solver_acceptable, kqp_pass, bar):
    """B0=P, B1=P∧S, B2=P∧K, B3=P∧S∧K"""
    if bar == "B0": return P
    if bar == "B1": return P and S
    if bar == "B2": return P and K
    if bar == "B3": return P and S and K
    raise ValueError(bar)
```

Sanity-tested against all 8 (P,S,K) combinations — monotonic nesting
holds across the B0→B1→B3 and B0→B2→B3 chains.

### 3.2 `replay_threshold_trajectories.py` — script (deterministic)

Inputs:
- `experiments/results/M3_SolverKQP/<sid>/iter_<NN>/_iter_record.json`
- (fallback) `experiments/results/M3_SolverKQP/<sid>/repair_summary.json::iter_records_summary`

Outputs:
- `experiments/reports/threshold_sensitivity_analysis.json`
- `experiments/reports/threshold_sensitivity_report.md` (human-readable, includes the §13.5 caption warning that `own_bar_stop_rate` is NOT comparable across bars, and the §13.6 upper-bound caveat)

The script:
1. Iterates every M3 sample's stored trajectory.
2. For each bar B ∈ {B0, B1, B2, B3}:
   - `stop_iter_B(i) = min{k : B(C_{i,k}) = True}` else 3 (§13.4 ran-out-of-budget clamp).
   - `final_quality_B(i) = B3(C_{i, stop_iter_B(i)})` — common-bar quality yardstick.
3. Aggregates per bar into the §13.5 central table.
4. Calls `_interpret_table` (B0→B3 gap + B1↔B2 delta + verdict) to gate §13.7.

CLI:
```bash
python experiments/replay_threshold_trajectories.py
                              [--m3-root PATH]
                              [--gap-trigger 0.10]
                              [--trigger-n0-n3]
```

### 3.3 `benchmark_config_v0.2.json::secondary_analysis`

Frozen as a config-level artefact listing the bars, monotonicity,
replay-script path, output paths, gap-trigger threshold, and the
N0–N3 conditional matrix (from §13.7).  Treats N0–N3 as **config-only
definitions** — the actual N0–N3 simulator is deferred per the contract
"decision gate" rule (§13.7).

### 3.4 Proxy probe (`probe_llm_connectivity`)

Added to `run_benchmark_v0.2.py` per §12 reproducibility rules:

- Default: bypass system proxy (`proxies={"http": None, "https": None}`)
  to avoid the silent 127.0.0.1:7890 dead-proxy trap that hit during
  the v0.1 batch.
- Override: set `REQUESTS_USE_PROXY=1` to use the system proxy.
- Bypass entirely: pass `--skip-probe` on the CLI (rare, used only for
  CI dry-run).
- On failure: prints the actual error class (`ProxyError`,
  `ReadTimeout`, `ConnectionRefused`) so the operator can act on it;
  aborts with `sys.exit(2)` so the run does not proceed with silent
  offline fallback.

### 3.5 `bar_pass` already integrated in `run_one_sample` results

Every iter's `run_result.iter_records[*]` already carries the three
component values needed by §13:

```python
{
  "iter": 0,
  "pipeline_valid": true|false,      # §4.2 P
  "solver_status": "fully_constrained|under_constrained|...|invalid",
  "solver_acceptable": true|false,   # §4.2 S  (canonically true iff status ∈ SOLVER_VALID_STATES)
  "kqp_pass": true|false,            # §4.2 K
  ...
}
```

`bar_pass(P, S, K, bar)` is therefore a pure function over the stored
artefacts — no recomputation, no re-execution, no LLM call.  This is
the core property that makes §13 a **zero-cost** analysis.

---

## 4. Acceptance checklist (§13.9 verbatim)

| §13.9 item | Where verified | Status |
|---|---|:---:|
| (1) 4 bars B0–B3 monotone nested (`B0 ⊆ B1 ⊆ B3`, `B0 ⊆ B2 ⊆ B3`) | `bar_pass` exhaustive truth table | ✅ |
| (2) replay reuses M3 stored artefacts only (no new LLM) | `load_trajectory` reads `_iter_record.json`; no LLM call in `replay_*` | ✅ |
| (3) central table reports **both** own-bar (non-comparable) + common-bar (comparable) with caption | `render_markdown` produces the §13.5 dual-column table + caption | ✅ |
| (4) over-trust upper-bound caveat included in writeup | `interp['caveat']` baked into `_interpret_table`; printed at top of `.md` | ✅ |
| (5) N0–N3 gated behind gap condition; not in default plan | `n0_n3_triggered = (gap ≥ 0.10) or force_n0_n3_flag`; config documents the decision gate | ✅ |

§11 acceptance item 11: "Secondary analysis (§13 stop-bar
sensitivity) protocol documented; it is post-hoc on M3 artefacts,
gated, and does not block the main ablation." — implemented via
`benchmark_config_v0.2.json::secondary_analysis` plus the standalone
replay script.

---

## 5. Smoke test (1 sample, 1 method)

Run with the v0.2 M3 smoke-test artefact (a single sample that did not
meet any bar at any iteration):

```text
[replay_threshold_trajectories] wrote …/threshold_sensitivity_analysis.json
[replay_threshold_trajectories] wrote …/threshold_sensitivity_report.md
Own-bar stop rates:  [(B0, 0.0%), (B1, 0.0%), (B2, 0.0%), (B3, 0.0%)]
Common-bar (B3) quality: [(B0, 0.0%), (B1, 0.0%), (B2, 0.0%), (B3, 0.0%)]
Interpretation: small_gap (B0→B3 gap=0.0); N0–N3 triggered=False
```

The numbers are not meaningful yet (n=1, all bars fail), but the
mechanics are verified:

- load_trajectory → 2 iter records (iter_00 + iter_01)
- per-bar replay → returns `stop_iter=1` for every bar (clamp to last seen)
- common-bar quality → `B3(P=False, S=True, K=False) = False`
- interpretation → `small_gap` (0.0 < 0.10 threshold) → N0–N3 **not** triggered

The script ran in <1 second — confirming **§13.8 zero-cost claim**.

---

## 6. What remains (post-M3)

After the main M0–M3 batch completes (currently blocked by LLM
connectivity, see §7), re-run `replay_threshold_trajectories.py` on the
full M3 trajectory:

```bash
"D:/Anaconda/envs/cad_subproject1/python.exe" \
    experiments/replay_threshold_trajectories.py \
    --m3-root experiments/results/M3_SolverKQP
```

Expected output range (104 eligible negatives):

| Bar | own-bar stop rate (descriptive) | **common-bar quality** | quality gap vs B3 | token savings |
|---|:-:|:-:|:-:|:-:|
| B0 | ~95–100% (code runs for almost all) | ~5–20% (most fail B3) | large? |  large |
| B1 | ~85–95% | mid | mid | mid |
| B2 | ~85–95% | mid-high | mid | mid |
| B3 | ~30–60% (this is M3 Success@3) | ~30–60% (= M3) | 0 | 0 |

The real question §13 will answer empirically: **does B0 (just "code
runs") preserve B3-quality or lose substantial share to over-trust?**
If the B0→B3 gap is <10pp we document it as a "reassuring deployment
finding"; if >10pp we document it as "verifications are also gates,
not just feedback" and motivate §13.7 (current default: do not run it
per the decision gate).

---

## 7. Known caveats

1. **M3 trajectory depth.** The current `run_one_sample` runs max
   `iter_00 + iter_01 + iter_02 + iter_03 = 4` iters (init + 3 repair).
   §13.4 is written in terms of `k ∈ {0, 1, 2, 3}`.  When a sample
   triggers S3 at iter 1, the recorded trajectory has only iter_00 and
   iter_01.  The replay script handles this by **clamping** `stop_iter_B`
   to the last seen iter (so no out-of-range index is read).  When B3
   is met early, weaker bars may be met even earlier — the replay
   preserves this exactly as the trajectory records it.
2. **`k_met` for S4 (max_iter).** If a bar is never met (bar never
   True across the trajectory), `k_met=False` and `stop_iter_B=3`
   (clamp).  Same in §13.4 pseudocode.  The "own-bar stop rate" then
   reports the fraction of samples where the bar was ever met.
3. **Token-savings reading.** Each iter carries `input_tokens` +
   `output_tokens` (0 unless the LLM actually ran).  Summed up to
   `stop_iter_B` for each bar.  `mean_token_savings_vs_B3 =
   tokens_up_to_iter_B3 − tokens_up_to_stop`.  Currently All M0/M1/M2/M3
   smoke tests used offline fallback (0 tokens), so the token column
   is informational until real LLM runs land.
4. **M3 trajectory vs M0 trajectory.** §13 only replays M3's full
   trajectory (per §13.2 — only the bar effect is studied; feedback
   effect is the main ablation's territory).  Section §13.6 caveat
   ("upper-bound on real deployment quality") is enforced by the
   "M3 trajectory is full-feedback" caveat banner in the report.
