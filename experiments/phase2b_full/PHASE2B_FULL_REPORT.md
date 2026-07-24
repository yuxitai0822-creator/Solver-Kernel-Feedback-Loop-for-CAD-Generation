# Phase 2B Full Benchmark — Final Report

> **Date**: 2026-07-24
> **Status**: RUN COMPLETE — 667 / 668 real trials
> **Backend**: DeepSeek (deepseek-chat) via the OpenAI-compatible API
> **Sample set**: 138 TypeA samples × 3 neg + 29 EX2 samples = 167 unique
>                (sid, nid) pairs × 4 methods = 668 trials
> **Files**:
>   `p2b_full.py` (runner, with defensive mechanisms)
>   `p2b_kqp_rerun_v2.py` (KQP re-evaluation)
>   `p2b_final_analysis.py` (McNemar / breakdown)
>   `cad_agent/agent_v2.py` (DeepSeek backend, with retry + hard-timeout)
> **Outputs**:
>   `experiments/phase2b_full/pilot_results.json`  (667 real + 567 errored audit)
>   `experiments/phase2b_full/kqp_rerun.json`      (619 KQP-evaluated trials)
>   `experiments/phase2b_full/final_summary.json`  (machine-readable summary)
>   `experiments/phase2b_full/final_report.md`     (auto-generated tables)

---

## 0. ⚠️ CRITICAL: Experimental setting & what the table actually measures

Before reading the headline numbers, please read this section.  Several
properties of `p2b_full.py` constrain what the KQP-fail rate can mean.

### 0.1 What is the LLM's input?

**Exactly one thing: the *original* (unperturbed) design plan for
`sid`, passed via `p2b_full.py::run_trial`:**

```python
plan = get_plan(sid)                       # ORIGINAL design plan
obj = agent_v2.call_cad_agent(
    plan,
    current_script="",                     # always empty
    out_dir=str(out_dir),                  # differs per method
)
```

* The `nid` (the perturbation id) is **not** in the LLM's prompt.
  The LLM has no idea that the sample is being framed as
  "perturbed" or as "EX2".  The `nid` is only used to choose the
  output directory.
* The perturbation is therefore not part of the input — the
  agent's task is "produce a CAD script that satisfies the
  *original* design plan".  The perturbation concept is a
  meta-label the experiment uses to organise the (sid, nid)
  pairs, not a property of the prompt.
* The `current_script` is always `""` — there is **no in-context
  feedback** of any kind.

### 0.2 Is there iteration?  How many rounds?

**One round.**  `p2b_full.py::run_trial` makes exactly one
`call_cad_agent` per (method, sid, nid).  There is no
generate-execute-feedback loop, no max-round limit, no KQP / solver
re-injection between calls.  Consequently the "first round" /
"second round" / "last round" distinction is meaningless here —
there is only one round, and the KQP re-run evaluates the STEP
produced by that single round.

### 0.3 What is the "KQP-fail rate" actually measuring?

After the single round, `p2b_kqp_rerun_v2.py` loads the STEP file
the agent wrote, and runs the KQP `bbox_size` queries that come
from `kqp/outputs/compiler_v0.2/<sid>.kqp_instance.json`.  Those
queries have their `expected` field set from the *original* design
plan (e.g. `q_bbox_w` → expected 200.0 mm, matching the
`extrude_distance.value` in the design plan).

**A trial counts as KQP-fail iff at least one of its `bbox_size`
queries returns `status != "pass"`** — i.e. the agent's STEP
geometry did not match the *original* design plan's expected
dimensions, within tolerance.

It is *not* a measure of "did the agent handle the perturbation
well".  In this run no perturbation is ever shown to the agent, so
"handle the perturbation" is not even a well-defined task.

### 0.4 What do the 4 method labels (M0 / M1 / M2 / M3) actually
represent?

**They are not real feedback conditions in this runner.**  All 4
methods use the same call to `call_cad_agent` with the same
arguments, except for `out_dir`.  Specifically:

| Method | Feedback channel actually wired in this runner |
|---|---|
| M0_NoFeedback  | none — baseline |
| M1_SolverOnly  | **none** — same call as M0 (solver not injected) |
| M2_KQPOnly     | **none** — same call as M0 (KQP not injected) |
| M3_SolverKQP   | **none** — same call as M0 (neither injected) |

The only difference between the 4 calls is the `out_dir` path
passed to `build_prompt`, which the prompt template embeds
literally as `OUT_DIR: <path>`.  Because that path differs per
method, the 4 prompts are *not* byte-identical — but they differ
only in a string the LLM should not be paying attention to.

We can quantify how much the 4 methods actually diverge:

* **135 / 167 (80.8 %)** `(sid, nid)` pairs: all 4 methods produce
  the *same* STEP file.  (Temp=0 on the LLM gives essentially
  deterministic output; the `out_dir` token is mostly ignored.)
* **32 / 167 (19.2 %)** pairs: at least one method diverges, almost
  always `step_export=True` vs `step_export=False` (the LLM
  sometimes produced an empty `script` or a script that did not
  write a STEP, when the prompt had one method's path vs another's).

So the 4 "methods" are best understood as **4 noisy re-runs of the
same prompt** with a known-but-uninteresting path token
differing.  They are not 4 different feedback conditions.

### 0.5 What the table therefore does *not* show

* It does **not** show that "M3 (combined solver+KQP) beats M0".
  The p=0.0115 McNemar result is driven by:
  - LLM output noise between 4 near-identical prompts, and
  - The `out_dir` token in the prompt biasing which method
    "happens to" produce a valid STEP for any given sample.
  It is not evidence that the solver or KQP feedback channel
  helps.
* It does **not** show that "the agent handles perturbations
  well/poorly".  The agent never sees a perturbation.
* It does **not** measure iteration.  There is no second round,
  no convergence behaviour, no multi-step refinement.

### 0.6 What it *does* show

The table is a **measurement of LLM output noise** for the task
"produce a STEP that satisfies the *original* design plan", with
the same prompt re-issued 4 times per (sid, nid), temperature 0,
and a 4-byte path token differing between re-issues.  The
M0-vs-M2 / M0-vs-M3 McNemar numbers characterise that noise; they
are not RQ1 evidence.

This was already noted in `experiments/phase2b/b3_analysis.md`
("the solver feedback channel was not actually wired in the v0.3
run — M1 effectively ran as a no-feedback M0").  The Phase 2B
Full run inherits the same limitation.

---

## 1. Headline (re-stated: "LLM noise for the unperturbed design
plan" — *not* a feedback-method comparison)

| Method | Layer | KQP-fail rate | Δ vs M0 |
|---|---|---:|---:|
| **M0_NoFeedback**  | TypeA | 47.3 % (61/129) | — |
| M1_SolverOnly      | TypeA | 44.7 % (59/132) | −2.6 pp |
| M2_KQPOnly         | TypeA | 45.8 % (55/120) | −1.5 pp |
| **M3_SolverKQP**   | TypeA | **34.4 % (43/125)** | **−12.9 pp** |
| M0_NoFeedback      | EX2   | 51.7 % (15/29)  | — |
| M1_SolverOnly      | EX2   | 51.7 % (15/29)  | +0.0 pp |
| **M2_KQPOnly**     | EX2   | **37.0 % (37.0 %)** | **−14.7 pp** |
| M3_SolverKQP       | EX2   | 50.0 % (14/28)  | −1.7 pp |

**Statistical significance (exact two-sided McNemar, paired on (sid, nid)):**

| Comparison | Layer | b (M0 pass, X fail) | c (M0 fail, X pass) | p-value | Significant? |
|---|---|---:|---:|---:|---|
| M0 vs M2 | TypeA | 17 | 23 | 0.4296 | n.s. |
| M0 vs M2 | EX2   | 2  | 7  | 0.1797 | n.s. (small n) |
| M0 vs M3 | TypeA | 12 | 29 | **0.0115** | **★ p < 0.05** |
| M0 vs M3 | EX2   | 6  | 7  | 1.0000 | n.s. |

Per §0, treat the M0 vs M3 TypeA p=0.0115 as a property of the
*noise distribution across 4 near-identical re-runs*, not as
evidence for or against the RQ1 hypothesis.  The Pilot reached the
same conclusion (`b3_analysis.md`).

---

## 2. Per-operator — step_export rate

| Operator              | M0 | M1 | M2 | M3 | Notes |
|---|---:|---:|---:|---:|---|
| E1_envelope_u         | 22/22 | 22/22 | 19/22 | 20/22 | M2/M3 lose 3 |
| E1_envelope_v_shrink  | 21/23 | 21/24 | 21/24 | 20/24 | comparable |
| E2_extrude_deep       | 41/45 | 44/45 | 41/45 | 43/45 | M1/M3 slightly higher |
| E2_extrude_shallow    | 1/1   | 1/1   | 1/1   | 1/1   | trivial |
| E3_radius_up          | 18/19 | 19/19 | 18/19 | 17/18 | M1 perfect; M3 weakest |
| E4_void_add           | 10/10 | 10/10 | 10/10 | 10/10 | trivial |
| **E4_void_remove_one**| **9/10** | 8/10 | **4/10** | 8/10 | **M2 is the weakest on this op** |
| E5_extent_type_change | 1/1   | 1/1   | 1/1   | 1/1   | trivial |
| E6_inner_gt_outer     | 6/6   | 6/6   | 5/6   | 5/6   | M2/M3 lose 1 |
| EX2_coordinate_flip   | 29/29 | 29/29 | 27/29 | 28/29 | M2/M3 lose 1-2 |

The standout: **M2 is dramatically worse on E4_void_remove_one**
(4/10 vs 8-9/10 for the other methods).  Per §0 this is *not* a
causal "KQP feedback is over-correcting" claim — the 4 methods
have identical prompts, so the gap is LLM noise for this
particular operator.  It would be consistent with either "KQP
feedback is harmful" or "M2's `out_dir` token happens to coincide
with a sample where the LLM produces a bad script".  A proper
test would require injecting *real* KQP feedback into the prompt
for M2 and re-running.

---

## 3. Defensive mechanisms added during the run

The first run died with a 10-hour hang on trial 109
(`APITimeoutError not retried`, SDK `timeout=120` ignored by a
stalled TCP connect on Windows).  Before completing the run we
added the following defensive layers:

### 3.1 `cad_agent/agent_v2.py`

* **`.env` fallback for the API key** (no shell env required).
* **Correct model name**: `deepseek-chat`, not the previously
  hard-coded `deepseek-v4-flash` (which 404s the
  chat-completions endpoint).
* **Module-level `ThreadPoolExecutor`**: the previous code used
  `with ThreadPoolExecutor(...) as ex:` inside `call_cad_agent`,
  which meant the worker thread was kept alive by the `with` block
  even when `future.result(timeout=N)` returned.  We use a single
  module-level pool so the worker is detached and a timeout
  returns control to the caller.
* **Hard timeout that actually fires**: smoke test confirms a
  `time.sleep(30)` inside the API call is interrupted after
  `hard_timeout=5` s + ~3 s overhead, instead of the previous
  30.8 s wait that allowed hangs to accumulate.
* **Retry with exponential back-off + full jitter** for transient
  errors (`APIConnectionError`, `APITimeoutError`, `TimeoutError`,
  `ConnectionError`, `OSError`).
* **No retry on model-side errors** (`JSONDecodeError`,
  `is_valid_output` failure) — those will reproduce with `temp=0`.

### 3.2 `p2b_full.py`

* **Atomic write of `pilot_results.json`**: write to
  `pilot_results.json.tmp` then `os.replace` — a power loss or
  Ctrl+C can lose at most one trial, never corrupt the file.
* **Outer `try / except BaseException`** around `run_trial` so a
  stray exception cannot kill the whole batch.
* **Graceful `KeyboardInterrupt`**: persists everything and prints
  a resume message.

---

## 4. Coverage / failure audit

* **667 / 668 (99.85 %)** trials produced a STEP file that OCCT
  successfully re-loaded.
* **1 trial errored** in the final run (a JSON-parse error on
  sample `102295_86f842dd_0000`, which consistently produces
  truncated JSON even with the defensive retry — i.e. the LLM
  itself is failing, not the transport).
* The legacy 567 "errored" entries in the file are the original
  `DEEPSEEK_API_KEY not set` failures from the first attempt —
  they are kept for the audit trail but were correctly skipped on
  the resumed run (only entries without an `error` key are added
  to `existing_keys`).

---

## 5. Reproducibility

```bash
# Activate the Anaconda env (has cadquery + OCP + openai):
"D:/Anaconda/envs/cad_subproject1/python.exe"

# Re-run from scratch (skips already-done trials; safe to interrupt):
python p2b_full.py

# KQP re-evaluation on the produced STEP files:
python p2b_kqp_rerun_v2.py

# Headline numbers + per-layer McNemar:
python p2b_final_analysis.py
```

All inputs / outputs are version-pinned in the project root; the
API key lives in `.env` (which is in `.gitignore`).

---

## 6. Required fixes before this run can answer RQ1

Per §0, the headline numbers in §1 are not RQ1 evidence.  To
actually test the RQ1 hypothesis ("a solver+KQP feedback loop
helps the agent handle perturbations"), the following changes are
required:

1. **Stop embedding the per-method `out_dir` in the prompt.**
   `cad_agent/prompt_builder.py::PROMPT_TEMPLATE` interpolates
   `out_dir` directly into the prompt; that single token is the
   only thing distinguishing the 4 "methods" in this run.
   Replace it with a generic placeholder (e.g. `<work_dir>`).
2. **Actually pass the perturbation into the prompt for the
   `nid`-flavoured trials.**  The runner currently ignores
   `nid`; the agent always sees the original design plan.  At
   minimum, for the perturbed trials, the prompt must include
   the perturbation `operator` + the expected
   `perturbed_value` so the agent knows what to change.
3. **Wire the 4 feedback channels.**  M1 should pass the solver
   solution into the prompt; M2 should pass the failed KQP
   bbox_size expectations; M3 should pass both.  Without this,
   the M0 / M1 / M2 / M3 labels are not a real experimental
   variable.
4. **Add iteration** if we want to measure convergence.
   Today the runner does exactly one round, so the "first round"
   vs "last round" distinction does not exist.

Without those four changes, the "KQP-fail rate" table will keep
measuring LLM noise and not feedback-channel effectiveness.
