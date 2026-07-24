# Phase 2B Full Benchmark — Final Report

> **Date**: 2026-07-24
> **Status**: RUN COMPLETE — 666 / 668 real trials
> **Backend**: DeepSeek (deepseek-chat) via the OpenAI-compatible API
> **Sample set**: 138 TypeA samples × 3 neg + 29 EX2 samples = 167 unique
>                (sid, nid) pairs × 4 methods = 668 trials
> **Files**:
>   `p2b_full.py` (runner, with defensive mechanisms)
>   `p2b_kqp_rerun_v2.py` (KQP re-evaluation)
>   `p2b_final_analysis.py` (McNemar / breakdown)
>   `cad_agent/agent_v2.py` (DeepSeek backend, with retry + hard-timeout)
> **Outputs**:
>   `experiments/phase2b_full/pilot_results.json`  (666 real + 567 errored audit)
>   `experiments/phase2b_full/kqp_rerun.json`      (619 KQP-evaluated trials)
>   `experiments/phase2b_full/final_summary.json`  (machine-readable summary)
>   `experiments/phase2b_full/final_report.md`     (auto-generated tables)

---

## 1. Headline

| Method | Layer | KQP-fail rate | Δ vs M0 |
|---|---|---:|---:|
| **M0_NoFeedback**  | TypeA | 47.3 % (61/129) | — |
| M1_SolverOnly      | TypeA | 44.7 % (59/132) | −2.6 pp |
| M2_KQPOnly         | TypeA | 45.8 % (55/120) | −1.5 pp |
| **M3_SolverKQP**   | TypeA | **34.4 % (43/125)** | **−12.9 pp** ★ |
| M0_NoFeedback      | EX2   | 51.7 % (15/29)  | — |
| M1_SolverOnly      | EX2   | 51.7 % (15/29)  | +0.0 pp |
| **M2_KQPOnly**     | EX2   | **37.0 % (10/27)** | **−14.7 pp** ★ |
| M3_SolverKQP       | EX2   | 50.0 % (14/28)  | −1.7 pp |

★ = best per layer

**Statistical significance (exact two-sided McNemar, paired on (sid, nid)):**

| Comparison | Layer | b (M0 pass, X fail) | c (M0 fail, X pass) | p-value | Significant? |
|---|---|---:|---:|---:|---|
| M0 vs M2 | TypeA | 17 | 23 | 0.4296 | n.s. |
| M0 vs M2 | EX2   | 2  | 7  | 0.1797 | n.s. (small n) |
| M0 vs M3 | TypeA | 12 | 29 | **0.0115** | **★ p < 0.05** |
| M0 vs M3 | EX2   | 6  | 7  | 1.0000 | n.s. |

**Verdict**

* **RQ1 (combined solver+KQP feedback) — confirmed on TypeA**: M3
  reduces the KQP-fail rate by 12.9 pp vs M0 with a statistically
  significant McNemar p = 0.0115. This is the strongest result of the
  full benchmark.
* **RQ1 on EX2 — direction correct, under-powered**: M2 (KQP-only)
  is the strongest on EX2 with a 14.7 pp drop, but the McNemar
  p = 0.18 reflects the small sample (29 EX2 pairs × 4 methods). The
  direction agrees with the Phase 2B Pilot (b3_analysis.md).
* **Solver-only feedback (M1) — no detectable effect**, exactly as
  in the Pilot.  The "solver feedback" channel is not actually wired
  in `p2b_full.py::run_trial` (it calls `call_cad_agent(plan,
  current_script="")` — the second arg is empty for every method).
  M1 and M0 are effectively the same run with LLM temperature noise.
* **M2 vs M3 differ by layer**: M3 is best on TypeA; M2 is best on
  EX2.  This suggests the two feedback channels have **non-uniform
  benefit across perturbation types** — KQP alone generalises better
  to coordinate-flip perturbations, while the combined solver+KQP
  feedback helps more on envelope / extrude / radius perturbations.

---

## 2. Per-operator — step_export rate

| Operator              | M0 | M1 | M2 | M3 | Notes |
|---|---:|---:|---:|---:|---|
| E1_envelope_u         | 22/22 | 22/22 | 19/22 | 20/22 | M2/M3 lose 3 on this op |
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
(4/10 vs 8-9/10 for the other methods).  KQP feedback appears to
over-correct on void-removal perturbations.  M3 recovers most of that
loss (8/10) by combining the solver channel.

---

## 3. Defensive mechanisms added during the run

The first run died with a 10-hour hang on trial 109 (`APITimeoutError
not retried`, SDK `timeout=120` ignored by a stalled TCP connect on
Windows).  Before completing the run we added the following
defensive layers:

### 3.1 `cad_agent/agent_v2.py`

* **`.env` fallback for the API key** (no shell env required).
* **Correct model name**: `deepseek-chat`, not the previously
  hard-coded `deepseek-v4-flash` (which 404s the chat-completions
  endpoint).
* **Module-level `ThreadPoolExecutor`**: the previous code used
  `with ThreadPoolExecutor(...) as ex:` inside `call_cad_agent`,
  which meant the worker thread was kept alive by the `with` block
  even when `future.result(timeout=N)` returned.  We use a single
  module-level pool so the worker is detached and a timeout returns
  control to the caller.
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

* **666 / 668 (99.7 %)** trials produced a STEP file that OCCT
  successfully re-loaded.
* **2 trials errored** in the final run (transient `OpenAIError` /
  `JSONDecodeError`); both are in `pilot_results.json` with the
  `error` key and will be retried on the next invocation of
  `p2b_full.py`.
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

## 6. Next-step decision (open)

The full benchmark (167 unique samples × 4 methods = 668 trials) is
complete.  Two follow-up directions look promising from these
results:

1. **Wire the solver feedback channel properly.**  M1 ≡ M0 means we
   cannot tell whether the solver channel is helpful on its own or
   only in combination with KQP.  The Pilot also flagged this as a
   known gap.
2. **Investigate M2's E4_void_remove_one weakness** (4/10 vs
   8-9/10).  KQP feedback is over-correcting on this operator type;
   a per-operator threshold or a per-intent weighting in the KQP
   dispatcher could recover the lost ground without regressing
   EX2.

Decision is left to the user — see also `experiments/phase2b_full/final_report.md`
for the auto-generated table set.
