# Pilot Test Protocol v0.1

> **Date**: 2026-07-16
> **Status**: READY TO RUN
> **Scope**: pre-full-benchmark smoke test on 24 sample-states × 4 methods
> **Owner**: execution agent
> **Contract ref**: `doc/experiment_contract_v0.1.md` §3, §4, §13; Task 3

---

## 0. Purpose

The pilot is NOT a statistical experiment. It is a **protocol smoke test**
with three goals, in priority order:

1. **Pipeline integrity** — confirm every component (adaptor → solver →
   KQP → agent → CED → Success computation → stop rules → artifact save)
   runs end-to-end on real LLM calls without crashing.
2. **Protocol fidelity** — confirm the four methods (M0–M3) behave as
   the contract §3/§4 specifies: shared verification pipeline, per-method
   feedback injection, three-way Success conjunction, S1–S4 stop rules.
3. **Artifact completeness** — confirm every per-iteration artifact in
   §10 is produced and parseable, so the post-run summarizer works.

The pilot is NOT intended to produce publishable Success@K numbers. With
24 samples per method the numbers are noise. Do not over-interpret them.

---

## 1. Why these samples — selection rationale

### 1.1 The core constraint: visibility coverage

The prevalidation report (`experiments/reports/ablation_study_prevalidation_report.md`)
established that the four feedback channels have **different visibility**
over the 104 eligible negatives:

| Channel | Visible subset | n |
|---|---|---|
| KQP-visible (E1/E2/E5) | bbox errors that KQP catches | 89 |
| Solver-visible (E3/E4 subset) | constraint/radius issues solver catches | 15 |
| KQP blind spot | samples where KQP all-pass but solver invalid | 15 |

A pilot that only draws from the KQP-visible majority would make M1
(solver-only) look trivially bad and tell us nothing about whether the
solver channel *works when it should work*. Conversely, a pilot of only
solver-visible samples would make M2 look weak.

**Therefore the pilot must stratify across visibility subsets**, not
random-sample. The point is to exercise each feedback channel on samples
where that channel is *supposed* to have leverage, so a "no signal"
result can be attributed to a bug rather than to a blind spot.

### 1.2 Selection grid: 18 negatives

Pick 18 negatives to cover three dimensions simultaneously:

| Stratum | n | Rationale |
|---|---|---|
| **KQP-visible, solver-blind** (E1 envelope / E2 extrude-depth) | 8 | The main battlefield (89/104). Confirms M2 actually uses KQP feedback to fix bbox errors; confirms M1 honestly NO_CHANGE-stops here. |
| **Solver-visible** (E3 radius / E4 void) | 6 | The minority (15/104). Confirms M1 actually uses solver feedback; confirms M2's blind spot is real. Must include ≥2 E3 (radius) and ≥2 E4 (void) to cover both solver-visible subtypes. |
| **Both-visible / edge** (E5 symmetry, or any E2 where solver also reacts) | 2 | Confirms M3's complementarity has *some* sample to show on. symmetric_about_plane has only 1 eligible — include it if it exists, else substitute an E2 where solver returns under_constrained. |
| **Pipeline-fragile** (samples that previously caused adaptor/export/OCCT issues) | 2 | Stress the pipeline itself, not the feedback. Pick from the 4 isolated samples or any sample with a known adaptor quirk. These test crash-resilience, not feedback value. |

**Totals**: 8 + 6 + 2 + 2 = 18 negatives.

Why 18, not fewer: McNemar needs paired disagreements to even compute;
with 18 we get a *readable* per-stratum count even if not significant.
Why not more: pilot cost = 18 × 4 methods × up to 3 iters × LLM calls;
keeping it at 18 keeps the pilot under ~1 hour of wall-clock.

### 1.3 Positive no-op samples: 6

Select 6 clean positives for the no-op stability arm. Selection criteria:

- **Geometric diversity**: not all rectangles — include ≥1 circle/annulus,
  ≥1 polygon, ≥1 stadium if clean ones exist.
- **Different complexity**: 2 simple (single sketch + extrude), 2 medium
  (multi-feature), 2 harder (multi-hole or non-trivial profile).
- **All must be KQP-passing on clean STEP** (they are clean samples, so
  this should hold by definition — but verify, because a clean sample
  whose reconstructed STEP KQP-fails would corrupt the no-op baseline).

The no-op arm asks: *when given a correct CAD, does each method leave it
alone?* The failure mode of interest is **over-repair** — the agent
"fixing" a non-problem and breaking it. 6 samples × 4 methods is enough
to detect gross over-repair (if 3/6 break, that's a red flag) but not
to measure its rate precisely.

### 1.4 How to materialize the sample lists

The execution agent should, before running anything:

1. Load `task5_negative_perturbation/reports/adaptor_run_summary.json`
   (this is what `list_valid_negatives()` reads).
2. For each row, read its perturbation type from the perturbation meta
   to classify it into E1/E2/E3/E4/E5/E6.
3. Apply the §1.2 grid to pick 18 sample_ids. Record the selection
   rationale per sample in `experiments/pilot/pilot_sample_selection.json`.
4. For positives, load `Reconstruction_results/clean_reconstruction_set.json`
   and pick 6 by the §1.3 criteria. Record in the same file.

**If the grid cannot be exactly filled** (e.g., fewer than 6
solver-visible eligible), document the shortfall and substitute from the
nearest stratum — but never let any stratum go to 0, because a 0-stratum
means that feedback channel is untested in the pilot.

---

## 2. Pre-flight checks (do these FIRST, ~5 min)

Run these before any LLM call. Each is a hard gate — fail stops the pilot.

### 2.1 LLM connectivity
```bash
python experiments/run_benchmark_v0.2.py --method M3_SolverKQP --limit 0 --skip-probe
```
(If `--limit 0` is rejected, use `--limit 1` with a throwaway sample and
Ctrl-C after the probe prints OK.) Expected: `[probe_llm_connectivity] OK status=200`.
If this fails, do NOT proceed — the entire pilot depends on real LLM calls.

### 2.2 CAD backend sanity
Confirm the two hardcoded Python envs exist and can import cadquery / OCP:
```bash
"D:/Anaconda/envs/cad_subproject1/python.exe" -c "import cadquery, OCP; print('cadquery OK')"
"D:/Anaconda/envs/freecad_sketcher/python.exe" -c "import FreeCAD; print('freecad OK')"
```
Both must print OK. The adaptor subprocess uses the cadquery env; the
solver uses the freecad env (per `run_benchmark_v0.2.py` L74-75).

### 2.3 Frozen-input presence
Confirm the four input dirs are non-empty and the manifest loads:
```bash
python -c "import json; from pathlib import Path; \
  r=json.load(open('task5_negative_perturbation/reports/adaptor_run_summary.json',encoding='utf-8')); \
  elig=[x for x in r['rows'] if x.get('reconstruction_success')]; \
  print(f'eligible negatives: {len(elig)}'); \
  print('clean set:', len(json.load(open('Reconstruction_results/clean_reconstruction_set.json',encoding='utf-8'))['clean_samples']))"
```
Expected: eligible negatives ≥ 100; clean samples = 46. If the counts are
off, the frozen inputs have drifted — stop and reconcile before pilot.

### 2.4 Config- code alignment spot-check
Confirm v0.2 reads the v0.2 config (not v0.1) and that all four methods
are present with the right inject flags:
```bash
python -c "import json; c=json.load(open('experiments/config/benchmark_config_v0.2.json',encoding='utf-8')); \
  [print(m['id'], 'inject_solver=',m['inject_solver_feedback'], 'inject_kqp=',m['inject_kqp_feedback'], 'run_solver=',m['run_solver_feedback'], 'run_kqp=',m['run_kqp_feedback']) for m in c['methods']]"
```
Expected: M0 inject_solver=False inject_kqp=False; M1 True/False; M2 False/True; M3 True/True — and ALL four have run_solver=True run_kqp=True (the shared pipeline).

---

## 3. Execution plan

### 3.1 Output layout
```
experiments/pilot/
  pilot_sample_selection.json     ← §1.4 selection record
  runs/
    M0_NoFeedback/<sample_id>/... ← per §10 artifact tree
    M1_SolverOnly/<sample_id>/...
    M2_KQPOnly/<sample_id>/...
    M3_SolverKQP/<sample_id>/...
  pilot_summary.json              ← aggregate across methods
  pilot_failure_analysis.md       ← §5 failure log
  pilot_go_no_go.md               ← §6 decision record
```

### 3.2 Negative repair arm — run order

Run methods in this order: **M2 → M1 → M0 → M3**.

Rationale: M2 (KQP-only) exercises the most samples (8 KQP-visible) and
is the most likely to produce a success, giving early signal that the
pipeline works. M1 (solver-only) exercises the minority stratum. M0
confirms the blind baseline. M3 last, because it's the most expensive
(full feedback) and if M0–M2 revealed a bug, we fix before spending M3
tokens.

For each method, run all 18 negatives:
```bash
python experiments/run_benchmark_v0.2.py \
  --method M2_KQPOnly \
  --sample <sid1> --sample <sid2> ... --sample <sid18> \
  --out-root experiments/pilot/runs/M2_KQPOnly \
  --config experiments/config/benchmark_config_v0.2.json
```
(If the `--sample` list is too long for the shell, write the 18 ids to
a file and have the execution agent expand them. Do NOT use `--limit 18`
— that takes the *first* 18 eligible, which won't match the §1.2 grid.)

Repeat for M1, M0, M3 with the same 18 sample_ids.

### 3.3 Positive no-op arm

**Important caveat**: `run_benchmark_v0.2.py` currently only exposes the
negative-repair CLI path (`run_one_sample` always applies
`perturb_ir_canonical`). There is **no positive no-op CLI** in v0.2 yet.

Two options for the pilot:

- **Option A (recommended for pilot)**: defer the no-op arm. The pilot's
  primary goal is pipeline integrity on the repair path; no-op stability
  can be tested once the no-op path exists. Record this as a known gap
  in `pilot_go_no_go.md`.
- **Option B (if a no-op entry point is added quickly)**: run the 6
  positives through a no-op mode that feeds the *clean* IR (not perturbed)
  and checks the agent leaves it unchanged. This requires a small code
  addition (a `--no-op` flag that skips `perturb_ir_canonical`).

**Decision**: default to Option A. The no-op arm is a stability
*supplement*, not a pipeline-integrity test. If the repair arm passes,
the pipeline is proven; no-op can wait for its own entry point.

### 3.4 Token / time budget

- Per sample-method: up to 3 iters × ~3k input + ~1k output tokens ≈ 12k tokens.
- 18 negatives × 4 methods = 72 runs × 12k ≈ **860k tokens** total.
- Wall-clock: ~30–60 s per run (dominated by LLM + CAD subprocess) →
  72 × 45 s ≈ **55 min**. Budget 90 min to be safe.

If token cost is a concern, reduce to M2 + M0 only (18 × 2 = 36 runs,
~430k tokens) — this still proves the pipeline and the feedback-injection
difference, just doesn't exercise M1/M3. But all four is preferred.

---

## 4. What to verify during the run

After each method completes its 18 samples, check these BEFORE starting
the next method. A failure here means stop and diagnose.

### 4.1 Per-sample run_result.json exists and parses
```bash
python -c "import json,glob; \
  [print(f, 'OK') for f in glob.glob('experiments/pilot/runs/M2_KQPOnly/*/run_result.json')][:3]"
```
Every sample dir must have a parseable run_result.json.

### 4.2 Stop-rule distribution looks sane
For each method, tally `final_status` / `stop_reason` across 18 samples.
Expected patterns (from §3.6 of the contract):

| Method | Dominant expected stop | Red flag |
|---|---|---|
| M0 | mostly S1 (no_change) on KQP-visible samples | S3 success on many → M0 is leaking feedback |
| M1 | S1 on the 8 KQP-visible; some S3 on the 6 solver-visible | S1 on *all* 18 → solver feedback not injected |
| M2 | some S3 on the 8 KQP-visible; S1 on solver-visible blind spot | S1 on all 8 KQP-visible → KQP feedback not injected |
| M3 | most S3 where any channel has leverage | S1 everywhere → neither channel injected |

**The single most important pilot check**: M0 and M2 should differ on
the 8 KQP-visible samples. If M0 and M2 have identical stop distributions
on those 8, the feedback injection is broken.

### 4.3 Success definition is the three-way conjunction
Spot-check 3 run_results per method: confirm `final_status.success` ==
`pipeline_valid AND solver_acceptable AND kqp_pass` at the final iter.
If `success=True` but `solver_acceptable=False`, the code has reverted to
KQP-only success — a regression.

### 4.4 Artifacts complete per §10
For 2 samples per method, confirm the iter dir has all of:
`IR_t.json, IR_t1.json, ced.json, solver_feedback.json, kqp_feedback.json,
generated_script.py, generated.step, agent_request.json, agent_response.json,
timing.json`. Missing artifacts break the post-hoc §13 analysis.

### 4.5 CED is non-trivial
On samples where the agent actually repaired (ir_was_modified=True),
`ced.json` must have `ced_declared.raw > 0`. If all CEDs are 0 but the
agent claimed to repair, the CED diff is broken.

### 4.6 M0 actually called the agent
Confirm M0's iter_01 has a non-empty `agent_request.json` and
`agent_response.json`. If M0 produced empty agent artifacts, the code
reverted to the old "M0 open-loop no-op" behavior (contract violation).

---

## 5. Failure handling during the pilot

The pilot is expected to surface failures. That's its job. Classify each:

| Class | Meaning | Action |
|---|---|---|
| **F-infra** | adaptor/solver/KQP subprocess crash, OCP load fail, STEP export fail | Log in pilot_failure_analysis.md; if >3 samples hit the same infra failure, stop and fix before continuing |
| **F-llm** | LLM timeout, 429 rate limit, malformed JSON response | Log; if >20% of calls fail, the LLM config needs adjustment (timeout, retries) |
| **F-protocol** | success=True with solver invalid (§4.3 regression), M0 not calling agent, feedback leaking across methods | **STOP the pilot** — this is a contract violation, not a data point |
| **F-data** | sample's clean IR missing, KQP instance missing, design plan missing | Log; exclude sample from pilot summary, substitute from same stratum |

**Rule**: F-protocol failures are hard stops. The others are logged and
the pilot continues (unless they exceed the thresholds above). The point
of the pilot is to find F-protocol issues before the full 104×4 run.

---

## 6. Go / No-Go decision (post-pilot)

After all four methods complete on the 18 negatives, write
`experiments/pilot/pilot_go_no_go.md` with a verdict:

### Go criteria (ALL must hold)
1. **No F-protocol failures** — success definition, feedback isolation,
   M0 agent call all conform to contract.
2. **M0 ≠ M2 on KQP-visible stratum** — the 8 KQP-visible samples show
   different stop/success patterns between M0 and M2 (proves feedback
   injection works).
3. **≥90% of runs produced a parseable run_result.json** — infra is stable.
4. **All four methods completed** on all 18 samples (or documented
   F-infra/F-data exclusions).
5. **Artifacts complete** on the spot-checked samples (§4.4).

### No-Go triggers (ANY → stop before full benchmark)
- Any F-protocol failure.
- M0 and M2 statistically indistinguishable on the KQP-visible stratum
  (feedback injection broken).
- >20% F-infra rate (pipeline not stable enough for 104×4).
- Success=True observed with solver_acceptable=False (success regression).

### If No-Go
Diagnose, fix in `run_benchmark_v0.2.py` or config, re-run only the
affected method/stratum. Do NOT proceed to the full benchmark until the
pilot goes Go.

### If Go
The full benchmark (Task 4) can proceed on the 104 eligible negatives
with all four methods. The pilot's per-stratum numbers are *not* carried
forward — the full run re-runs everything from scratch on the full set.

---

## 7. What the pilot does NOT decide

- **No statistical conclusions** — 18 samples cannot support significance
  claims. Do not report pilot Success@K as if they were results.
- **No prompt tuning** — if the pilot reveals the prompt is weak, do NOT
  tweak it mid-pilot. Log it; prompt changes require re-freezing per §12.
- **No §13 threshold analysis** — that requires the full M3 trajectory;
  the pilot's M3 run is too small to meaningfully replay bars.
- **No per-intent inference** — even the full 104 set only supports
  inference on bbox_size; the pilot's per-intent cells are descriptive only.

The pilot's sole deliverable is a **Go/No-Go on protocol readiness**,
plus a failure log that informs the full-run plan.

---

## 8. Hand-off note to the execution agent

1. Read `doc/experiment_contract_v0.1.md` §3, §4 first — this is the
   source of truth for what "correct" means.
2. Do §1.4 sample selection and save to `pilot_sample_selection.json`
   before any run.
3. Do §2 pre-flight checks; halt on any failure.
4. Run §3.2 in order M2 → M1 → M0 → M3; after each method do §4 checks.
5. Classify all failures per §5; STOP on F-protocol.
6. Write `pilot_go_no_go.md` per §6.
7. Do NOT modify `run_benchmark_v0.2.py`, the config, or any frozen
   component during the pilot. If a bug is found, log it and stop —
   fixes happen in a separate step with version tracking.

If in doubt about whether something is F-protocol vs F-infra, treat it
as F-protocol (conservative) and escalate.
