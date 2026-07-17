# Experiment Contract v0.1 — Solver-KQP Repair Loop Benchmark

> **Date**: 2026-07-09
> **Status**: FROZEN
> **Purpose**: freeze inputs, components, metrics, success criteria, and artifact
>  protocols so the four-method ablation (M0 / M1 / M2 / M3) is reproducible and
>  comparable.

---

## 1. Frozen Inputs

| Input | Path | Size |
|---|---|---|
| 46 clean positive samples | `Reconstruction_results/clean_reconstruction_set.json` | 46 |
| 132 valid negative samples | `task5_negative_perturbation/.../perturbations/` (after reconstruction_success==true) | 132 |
| 138 total perturbation records | `task5_negative_perturbation/reports/adaptor_run_summary.json` | 138 |
| DesignPlan v0.6 instances | `DesignPlan/compiler/instances_v6/<sid>.design_plan.json` | 46 |
| KQP v0.2 instances | `kqp/outputs/compiler_v0.1/<sid>.kqp_instance.json` | 46 |
| Original Fusion360 history JSON | `Reconstruction_results/<sid>/input_history.json` | 46 |
| CAD IR v0.1 examples | `cad_ir/samples/manual_ir_examples/` | 48 |

Negative sample initial-failure status is determined by the KQP runner:
a negative sample is "initially failed" if at least one of its KQP queries
returns `status: fail` on iter 0 (the unperturbed-GT STEP).  We use the
138 perturbation records; some have been pre-built (CED_S1/2, ED_S1/2) — for
the benchmark we re-run KQP feedback on the perturbed STEP to confirm initial failure.

---

## 2. Frozen Components (versions)

| Component | Version | Path |
|---|---|---|
| DesignPlan Schema | v0.6 | `DesignPlan/DesignPlan_schema06.txt` |
| DesignPlan Compiler | v6 | `DesignPlan/compiler/design_plan_compiler.py` |
| KQP Instance Schema | v0.2 | `kqp/kqp_schema_v0.2.txt` |
| KQP Compiler | v0.1 | `kqp/compiler/` |
| KQP Runner | v0.1 | `kqp/runner/` |
| Reconstruction Engine | v0.1 | `reconstruction_engine/` |
| Reconstructed STEP files | — | `Reconstruction_results/<sid>/generated.step` |
| Frozen Solver Feedback (FreeCAD) | v0.1 | `Freecadsolver_feedback/` |
| CAD IR Schema | v0.1 | `cad_ir/schema/cad_ir_schema_v0.1.json` |
| CAD IR Validator | v0.1 | `cad_ir/validator/validator.py` |
| CAD IR Adaptor | v0.1 | `cad_ir/adaptor/` |
| CED module | v0.1 | `cad_edit_distance/` |
| Repair Loop | v0.1 | `cad_repair_loop/` |
| LLM backend | ZHIPU glm-5.1 (temperature 0.0) | `https://open.bigmodel.cn/api/paas/v4/` |

See `doc/frozen_components_for_repair_benchmark.md` for full details.

---

## 3. Four Feedback Methods (M0 / M1 / M2 / M3) — DEFINITIVE

All methods share the same Code Agent prompt skeleton, same LLM
(ZHIPU glm-5.1), same temperature (0.0), same max_iter (=3), same LLM
timeout (120 s), same repair-loop skeleton, same verification pipeline.
They differ ONLY in which **diagnostic** feedback channels (solver /
KQP) are injected into the agent prompt.

Overall Structure:
                ┌──────────────────────────────────┐
                │   一个统一的 run_one_sample()     │
                │   4 个方法都过同一条流水线         │
                │   唯一变量：哪些 channel 进 prompt │
                └──────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
      Stage 1: Adaptor        Stage 2: Solver        Stage 3: KQP
      (永远跑，写 STEP)        (永远跑)               (永远跑)
                                    │                       │
                                    ▼                       ▼
                              solver_feedback.json   kqp_feedback.json
                              (永远存盘)              (永远存盘)
            │
            │  
            ▼
            Stage 4:  compute_success()  ──────────────────►  ★ 不进入 Stage 5
            测 Success(C) = PipelineValid ∧ SolverValid ∧ KQPSamplePass
            │  
            │ 
            ▼
            Stage 5: build_prompt() ── 把 method 允许的 channel 块拼到 [FEEDBACK]
            │       inject_solver_feedback? → 加 solver 子块
            │       inject_kqp_feedback?     → 加 kqp 子块
            │       总是加 pipeline 子块
            ▼
            Stage 6: validate_ir + compute_ced
            │
            ▼
            Stage 7: 检查 S1/S2/S3/S4 决定 break 还是 continue

### 3.1 Design philosophy

**(a) Proposition focus.** This experiment studies the effectiveness of
*solver constraint feedback* and *kernel (KQP) geometric-intent
feedback* on CAD repair. It does NOT study LLM self-correction, agent
architecture, or prompt engineering. The agent, LLM, temperature, prompt
skeleton, and iteration budget are identical across methods; the ONLY
variable is the feedback signal source.

**(b) Additive ablation over a shared base.** The four methods form a
monotonically increasing signal-richness gradient. **Pipeline execution
feedback is the shared base for ALL methods**, not a research variable.
It only answers "can the IR compile / execute / export STEP" — an
infrastructure-level crash signal. Solver and KQP are the *diagnostic*
feedbacks under study:

```
M0  Pipeline feedback only              (base: does the code run?)
M1  Pipeline + Solver feedback           (+ are constraints constructible?)
M2  Pipeline + KQP feedback              (+ is geometric intent met?)
M3  Pipeline + Solver + KQP feedback     (full diagnostics)
```

The ablation deltas are each clean:

| Delta | Question answered |
|---|---|
| M1 − M0 | marginal value of solver feedback |
| M2 − M0 | marginal value of KQP feedback |
| M3 − M2 | marginal value of solver on top of KQP |
| M3 − M1 | marginal value of KQP on top of solver |
| M3 − M1 − (M2 − M0) | interaction effect of the two feedbacks (if identifiable) |

**(c) LLM self-verification is explicitly excluded.** No self-eval loop
is inserted into any method. Reasons: (1) it adds an uncontrolled
variable that blurs the main proposition; (2) LLM self-eval capability
is an independent research question; (3) M0's baseline is "no diagnostic
feedback" — LLM self-eval is itself a diagnostic signal, so including it
would contaminate the clean base.

### 3.2 Unified prompt skeleton (shared by all four methods)

Each iteration the agent receives:

```
[DESIGN PLAN]   — frozen Design Plan v0.6 (visible to all methods; it is
                   the task spec, NOT the answer — KQP itself is compiled
                   from it)
[CURRENT IR]    — current CAD IR (iter 0 = initial negative IR;
                   iter k = post-repair IR from previous round)
[FEEDBACK]      — method-specific feedback (the ONLY variable; see §3.3)
[INSTRUCTION]   — identical instruction across all methods
```

Unified instruction (verbatim identical across methods):

```
You are a CAD repair agent. Based on the Design Plan, the current CAD IR,
and the feedback provided, either:
- Propose repair operations to fix identified issues, or
- Output NO_CHANGE if you believe no further repair is needed.

Output format (JSON):
{
  "action": "repair" | "no_change",
  "repair_operations": [
    {"op": "MODIFY|ADD|DELETE|REORDER", "target": "...", "field": "...",
     "old": ..., "new": ...}
  ]
}
```

### 3.3 Per-method definition

#### M0 — No (diagnostic) Feedback

**Design intent.** Establish the "no diagnostic feedback" baseline. The
agent only knows whether the IR compiles / executes / exports (pipeline
crash signal) and sees pipeline error messages; it does NOT know whether
constraints are satisfiable nor whether geometric intent is met. M0
answers: *with only runtime-crash feedback and the Design Plan spec, can
the LLM repair CAD?*

**`[FEEDBACK]` content** — pipeline result only:

```json
{
  "pipeline": {
    "compile":     "pass | fail",
    "execute":     "pass | fail",
    "step_export": "pass | fail",
    "occt_load":   "pass | fail",
    "error_messages": ["<full pipeline error text, if any>"]
  }
}
```

For the 104 eligible negatives the initial pipeline usually passes
(perturbations are parameter-level, not compile-breaking), so at iter 1
M0 receives "pipeline: all pass, no errors" — no diagnostic signal
points at the error. Whether M0 can repair then depends on the LLM's
prior ability to cross-check Design Plan params against IR params. If
the agent finds no discrepancy → NO_CHANGE → stop → fail. This is an
honest result.

#### M1 — Solver Only

**Design intent.** Measure the marginal value of solver constraint
feedback. On top of pipeline feedback the agent additionally receives
solver satisfiability diagnostics. M1 answers: *can constraint-solver
feasibility feedback help the LLM repair CAD?*

**`[FEEDBACK]` content** — pipeline + solver:

```json
{
  "pipeline": { ... },                 // same as M0
  "solver": {
    "status": "fully_constrained | under_constrained | conflict | invalid | solver_failure",
    "acceptable": true | false,
    "conflicts": ["..."],
    "invalid_constraints": ["..."]
  }
}
```

`acceptable = (status ∈ {fully_constrained, under_constrained})`. When
solver returns acceptable with no conflict/invalid, the solver feedback
gives NO diagnostic value for parameter-level errors (depth 15 vs 20),
and the agent tends to NO_CHANGE. Solver leverage is concentrated on
perturbations that create conflict/invalid. Per the prevalidation
visibility matrix, the solver-visible subset is only 15/104. **Expected:
M1 NO_CHANGE-stops at iter 1 on 89/104 samples.** This is NOT a design
flaw — it is the direct expression of solver-only feedback's structural
blind spot for geometric-intent errors.

#### M2 — KQP Only

**Design intent.** Measure the marginal value of KQP geometric-intent
feedback. On top of pipeline feedback the agent additionally receives
KQP design-intent compliance diagnostics. M2 answers: *can geometric
kernel-query feedback help the LLM repair CAD?*

**`[FEEDBACK]` content** — pipeline + KQP:

```json
{
  "pipeline": { ... },                 // same as M0
  "kqp": {
    "overall_pass": true | false,
    "queries": [
      {"query_id": "q_bbox_w", "intent": "bbox_size",
       "expected": 20.0, "observed": 15.0, "pass": false, "tolerance": 0.5}
    ]
  }
}
```

KQP feedback includes each query's intent/expected/observed/pass. The
`expected` value comes from the Design Plan compiler (NOT from GT), so
there is no leakage. KQP leverage covers 89/104 samples (E1/E2/E5) —
this is KQP's main battlefield. **Expected blind spot:** on the 15
solver-visible-only samples where KQP is all-pass but solver is invalid,
M2 sees "KQP all pass" → NO_CHANGE → stop → but SolverValid=False →
fail. M2 is the primary evidence source for RQ1.

#### M3 — Solver + KQP

**Design intent.** Measure the joint value of dual feedback and verify
the two feedbacks are complementary. M3 answers: *is Solver + KQP dual
feedback better than either single feedback?*

**`[FEEDBACK]` content** — pipeline + solver + KQP (full diagnostics):

```json
{
  "pipeline": { ... },                 // same as M0
  "solver":  { ... },                  // same as M1
  "kqp":     { ... }                   // same as M2
}
```

The order of solver and KQP in the `[FEEDBACK]` block is FIXED: solver
first, then KQP, identical for all samples and all iterations, to avoid
order effects. When solver is acceptable AND KQP is all-pass, the agent
naturally tends to NO_CHANGE — and if PipelineValid also passes this
coincides with Success (matches stop rule S3). M3's failures come mainly
from: (a) the repair operation itself being wrong (right direction,
wrong value); (b) pipeline-level failure (adaptor unsupported ops);
(c) invalid LLM output format.

### 3.4 Information-leakage boundary

| Information | M0 | M1 | M2 | M3 | Leakage verdict |
|---|---|---|---|---|---|
| Design Plan | ✓ | ✓ | ✓ | ✓ | safe — task spec; KQP is compiled from it |
| Current IR | ✓ | ✓ | ✓ | ✓ | safe — this is the object being repaired |
| Pipeline result + full error messages | ✓ | ✓ | ✓ | ✓ | safe — infrastructure signal, all methods see it in full |
| Solver result | ✗ | ✓ | ✗ | ✓ | safe — from the solver, not GT |
| KQP query result (incl. expected/observed) | ✗ | ✗ | ✓ | ✓ | safe — expected from Design Plan compiler |
| GT history JSON | ✗ | ✗ | ✗ | ✗ | **FORBIDDEN** — invisible to all methods |
| Clean IR | ✗ | ✗ | ✗ | ✗ | **FORBIDDEN** — may not overwrite with the correct answer |
| Perturbation metadata | ✗ | ✗ | ✗ | ✗ | **FORBIDDEN** — may not tell the agent the error type |
| Other method's feedback | ✗ | ✗ | ✗ | ✗ | **FORBIDDEN** — no cross-method visibility |

**Leakage audit requirement:** before the formal run, each method's
prompt is manually audited to confirm the `[FEEDBACK]` block contains
none of the FORBIDDEN rows above. The audit record is filed in the
experiment contract. Note in particular: **pipeline error messages are
visible in full to ALL methods** (including M0) — they help the LLM fix
IR syntax / adaptor / execution errors; only solver and KQP diagnostic
messages are gated by method.

### 3.5 Ablation logic & grouping requirements

The prevalidation report confirmed overall-mean comparisons are diluted
by signal blind spots. The main table MUST report simultaneously:

1. **Overall** (104 samples): Success@1/2/3, F2S, Mean Iter, CED, Runtime, Token.
2. **By error category** (E1–E6): Success@3, Targeted Repair Success, Mean CED.
3. **By KQP intent**: only `bbox_size` supports statistical inference;
   `through_void_count` / `cylinder_radius` / `symmetric_about_plane`
   are flagged "descriptive only"; `is_solid` is a hard gap (n=0 eligible).
4. **By visibility subset**:
   - solver-visible only (15 samples): M1 vs M0, M3 vs M2
   - KQP-visible only (89 samples): M2 vs M0, M3 vs M1
   - both-visible (intersection, if any): M3 complementarity evidence

**Statistical testing protocol:**
- Main table: McNemar test (paired, same sample across methods), report
  p-value and 95% CI.
- Per-intent: McNemar for `bbox_size` only; other intents report
  descriptive statistics (counts, proportions) flagged
  "n insufficient for inference".
- **Pre-registered "descriptive-only fallback":** when a subset has
  n < 30, report proportions only, do not claim significance.
- **Clustering:** the 132 negatives derive from 46 clean samples; the
  primary analysis treats the 104 eligible perturbations as independent
  intervention units, but the clean-level clustering effect is disclosed
  in the limitation section.

### 3.6 Expected behavior pattern (from prevalidation)

| Method | Expected stop pattern | Expected Success@3 shape | Expected CED shape |
|---|---|---|---|
| M0 | pipeline pass → no signal → NO_CHANGE (iter-1 stop) | very low; relies on LLM prior param cross-check | near 0 (unchanged) or high (blind large rewrite) |
| M1 | solver acceptable → NO_CHANGE (89 samples iter-1 stop) | low; concentrated on 15 solver-visible | low (mostly unchanged) |
| M2 | KQP all-pass → NO_CHANGE (15 samples iter-1 stop) | mid-high; concentrated on 89 KQP-visible | mid (targeted repair) |
| M3 | solver acceptable ∧ KQP all-pass → NO_CHANGE ≈ Success | highest; covers both subsets | lowest (most precise feedback → most local edit) |

**Key expected deltas:**
- M2 − M0: expected significant on the 89 KQP-visible subset (≥15pp, McNemar detectable).
- M1 − M0: needs ≥40pp on the 15 solver-visible subset to detect; overall likely not significant.
- M3 − M2: increment mainly from the 15 solver-visible samples; overall increment may be small.
- M3 vs M1: KQP increment from 89 samples; expected significant.

**Honest disclosure:** M1's overall Success@3 may be low. This is NOT a
design flaw but the structural blind spot of solver-only feedback for
geometric-intent errors. The paper explains this via by-error-category
grouping and the visibility matrix, attributing M1's low performance to
"the coverage boundary of solver feedback" rather than "solver feedback
is ineffective".

### 3.7 Prohibitions (method-level)

1. No mid-experiment modification of frozen components (KQP v0.2, Solver,
   Reconstruction Engine, CED rules, IR schema). A bug requires a version
   bump and re-run of the affected ablation.
2. No prompt tweaking to favor a method. All four share one base prompt;
   only the `[FEEDBACK]` block differs.
3. No using the Design Plan to "correct" the initial IR — the initial
   negative IR must faithfully reflect the perturbed state.
4. No using KQP failure info to auto-fix the initial IR at compile time.
5. No per-sample special-casing. All samples go through one pipeline.
6. No cross-method information sharing (M1 blind to KQP, M2 blind to solver, M0 blind to both).
7. No continuation after NO_CHANGE — S1/S2 stops immediately, no second chance.
8. Failed samples are NOT assigned a synthetic iteration count for Mean
   Iterations to Success; they do not participate in that mean.

---

## 4. Repair Loop Skeleton & Stop Rules (shared by all methods)

### 4.1 Verification pipeline (identical for ALL methods)

A critical rule: **the verification pipeline runs in full for every
method on every iteration, including M0.** Solver and KQP are always
executed and their results always recorded as artifacts. The ONLY thing
that changes by method is whether those results are *injected into the
agent's `[FEEDBACK]` block*. Running them unconditionally guarantees:

1. Success is computed under one uniform definition for all methods (fair comparison).
2. Full artifacts are recorded for failure attribution.
3. No method gets a different Success definition by "skipping" a check.

```
IR_{t+1}
  → [Adaptor]            → CAD script
  → [Execute]            → CAD document
  → [STEP export]        → STEP file
  → [OCCT load]          → occt_result
  → [Solver]             → solver_result      (always run, always saved)
  → [KQP]                → kqp_result         (always run, always saved)
  → Success(IR_{t+1}) = PipelineValid ∧ SolverValid ∧ KQPSamplePass
```

### 4.2 Success definition (frozen)

```
Success(C) = PipelineValid(C) ∧ SolverValid(C) ∧ KQPSamplePass(C)

PipelineValid = compile ∧ execute ∧ step_export ∧ occt_load all succeed
                (all modules run normally; compile + export succeed)

SolverValid   = solver.status ∈ {"fully_constrained", "under_constrained"}
                (under_constrained is treated as valid-but-not-optimal;
                 conflict / invalid / solver_failure are invalid)

KQPSamplePass = all mandatory KQP queries pass for this sample
```

This three-way conjunction is the PRIMARY success criterion
(`success`). A secondary, stricter criterion `strict_success` additionally
requires the solver to report no over-constraint warning, but the
PRIMARY reported metric uses the conjunction above. This replaces the
earlier draft's KQP-only primary: KQP-only success would have credited a
sample whose solver was in conflict, which is not a valid repair.

### 4.3 Stop rules (identical for ALL methods)

Four rules, applied identically to M0–M3:

```
S1  Agent outputs action = "no_change"      → STOP
S2  IR_{t+1} == IR_t (no actual change)     → STOP  (treated as NO_CHANGE)
S3  Success(IR_{t+1}) = True (measured)     → STOP  (efficiency cutoff;
                                              Success is NOT fed back to agent)
S4  max_iter = 3 reached                    → STOP
```

The rules are identical across methods; what differs is the *timing* at
which each method's agent decides to emit NO_CHANGE under its own
feedback signal — which is exactly what the ablation measures.

**S3 fairness note:** Success is a post-hoc measured value and is NOT
fed back to the agent (the agent only senses it indirectly through its
own feedback channel). S3's sole purpose is to prevent already-successful
samples from continuing to iterate and inflating RepairCost. All methods
benefit equally from this efficiency cutoff.

### 4.4 Iteration structure

```
iter 0: initial verification (no repair)
  input : initial negative IR_0
  action: run verification pipeline → record initial_status
  stop  : if Success(IR_0)=True → already-successful (negative samples
          should not be, but the protocol covers it)
  else  : proceed to iter 1

iter k (k = 1, 2, 3):
  input : Design Plan + IR_{k-1} + feedback_{k-1}
          feedback_{k-1} = method-specific feedback, sourced from the
          iter k-1 verification pipeline results
  action: agent outputs repair | no_change
  stop  : any of S1/S2/S3/S4 fires
  else  : IR_k = apply(repair, IR_{k-1}) → verify → proceed to iter k+1
```

### 4.5 Success@K bookkeeping

```
C_{i,0} = IR_0  (initial state; negative samples are always fail)

Success@1 = 𝟙[Success(C_{i,1})]                                    / N
Success@2 = 𝟙[∃k ≤ 2: Success(C_{i,k})]                            / N
Success@3 = 𝟙[∃k ≤ 3: Success(C_{i,k})]                            / N

Rules:
  if iter k triggers S1/S2 (NO_CHANGE), then C_{i,k} = C_{i,k-1} (unchanged)
  if iter k triggers S3   (success),    then Success@j (j≥k) = True
  if iter k triggers S4   (max_iter),   then C_{i,3} is the final state

Mean Iterations to Success = (1/N_success) × Σ k*_i
  where k*_i = min{k : Success(C_{i,k}) = 1}, computed ONLY over finally-
  successful samples. Failed samples do NOT participate (not recorded as
  4 or ∞) — this metric MUST be reported jointly with Success@K.
```

### 4.6 RepairCost (frozen)

```
RepairCost = Σ CED_declared  +  0.1 × n_execution  +  0.1 × n_verification
```

`n_execution` / `n_verification` are the counts of execution /
verification steps across the repair trajectory. Today execution and
verification are pure code runs (no token cost, negligible wall-clock),
so the two additive terms are placeholders that preserve **formal
consistency for the future**: when Phase 2 introduces an LLM into the
verification stage (and execution count grows with task complexity), the
counts can be replaced by token / time figures WITHOUT changing the
formula. CED_declared is the dominant term in Phase 1.

---

## 5. Repair Metrics (per task spec)

| ID | Metric | Definition |
|---|---|---|
| M1.1 | **Success@1** | Fraction of initial-failed samples whose `Success(C)=1` (§4.2: PipelineValid ∧ SolverValid ∧ KQPSamplePass) within 1 repair iteration. |
| M1.2 | **Success@2** | Same, within 2 repair iterations. |
| M1.3 | **Success@3** | Same, within 3 repair iterations (= final). |
| M1.4 | **F2S Conversion Rate** | # initial-failed that end success ÷ # initial-failed (= Success@3 numerically for a negatives-only set, but narratively distinct). |
| M1.5 | **Mean Iterations to Success** | Average (over finally-successful samples ONLY) of the first iteration k* where Success(C_k) = 1. Failed samples excluded. |
| M3.1 | **KQP Query Improvement** | ΔQPR = QPR_final − QPR_initial. |
| M3.2 | **Remaining Failed Query Count** | Mean / Median / P90 / Total of `∑ 1[query fail]` per sample, post-repair. |
| M3.3 | **Targeted Repair Success Rate (TRSR)** | For each negative, # targeted queries initially failed and finally passing ÷ # targeted. |
| M4.1 | **CED_declared** | Weighted operation-level edit distance between IR_t and IR_{t+1} (already implemented in `cad_edit_distance`). |
| M4.2 | **CED_executed** | Same on runtime traces. |
| M5.0 | **RepairCost** | `Σ CED_declared + 0.1×n_execution + 0.1×n_verification` over the repair trajectory. See §4.6 for the frozen formula and the rationale for the placeholder terms. |
| M6.0 | **Runtime Cost** | Wall-clock seconds per sample. |
| M7.0 | **Token Cost** | Σ input + output tokens consumed by the LLM. |

---

## 6. Generation Metrics (per task spec)

| ID | Metric | Definition |
|---|---|---|
| M8.1 | **Compile Success** | IR schema-valid AND adaptor successfully renders executable script. |
| M8.2 | **Execute Success** | Adaptor script runs end-to-end (no uncaught exception) and produces a body. |
| M8.3 | **STEP Export Success** | STEP file exists, size > 0, export API call returned successfully. |
| M8.4 | **OCCT Load Success** | `OCP.STEPControl_Reader` reads the STEP and returns a non-null shape. |
| M9.0 | **Solver / Sketch Validity** | Re-run Solver Feedback on the generated STEP (or its closest freeform equivalent); count samples where status ∉ {`conflicting`, `unsolvable`, `invalid_constraint_reference`}. |
| M10.0 | **KQP Sample Pass** | KQP `overall_status == "pass"`. |
| M11.0 | **KQP Query Pass** | Total # passed queries ÷ Total # queries (micro average). |
| M12.0 | **Per-intent Pass** | For each KQP intent (body_count, bbox_size, …), the query pass rate. |

---

## 7. Auxiliary Metrics (lower priority)

| ID | Metric | Definition |
|---|---|---|
| M13.1 | **CED_text** | Normalized Levenshtein over raw IR JSON.  Auxiliary only. |
| M13.2 | **Edit Efficiency** | `(KQP Query Improvement) / (RepairCost + ε)`.  Higher = more efficient. |
| M13.3 | **BBox Error** | Mean per-axis normalized BBox error vs. GT. |
| M13.4 | **Volume Error** | `|V_pred − V_GT| / (V_GT + ε)`. |
| M13.5 | **Chamfer Distance** | Mean bidirectional nearest-neighbor distance between sampled point clouds. |
| M13.6 | **IoU** | Volumetric intersection-over-union of the predicted solid vs. GT solid. |

---

## 8. Main-Indicator Hierarchy

**Generation question**: *Can the system construct a valid and intent-compliant CAD model?*
Pipeline → Solver/Sketch Validity → KQP Intent Compliance.

**Repair question**: *Can the system turn a failed CAD model into a valid one efficiently and with minimal edits?*
Success → Convergence → Quality Improvement → Minimal Editing → Cost.

The primary repair metric is **Success@3 (Success as defined in §4.2:
PipelineValid ∧ SolverValid ∧ KQPSamplePass, within ≤3 iterations)**,
with **CED_declared** as the primary editing-cost metric and
**RepairCost (§4.6)** as the trajectory-level cost metric. `strict_success`
(additionally requiring no over-constraint warning) is reported as a
secondary criterion. Generation metrics are reported per-method to
support the no-feedback baseline (M0) which can only be evaluated at the
initial generation level.

---

## 9. Result Schema

```json
{
  "method": "M2_KQP_only",
  "sample_id": "100243_9fb796fe_0005",
  "initial_success": false,
  "iter_records": [
    {"iter": 0, "pipeline_valid": false, "kqp_pass": false, "solver_status": "under_constrained",
     "solver_acceptable": true, "success": false,
     "agent_called": true, "ced_declared": 1.0, "ced_executed": 1.0,
     "n_execution": 1, "n_verification": 1,
     "wallclock_s": 4.3, "tokens": {"input": 2400, "output": 350}},
    ...
  ],
  "final_status": "success",
  "success": true,
  "strict_success": true,
  "n_iterations_to_success": 1,
  "final_kqp_pass_rate": 1.0,
  "remaining_failed_queries": 0,
  "ced_declared_trajectory": [1.0],
  "repair_cost": 1.2,
  "runtime_cost_s": 8.6,
  "token_cost_total": 2750
}
```

Notes on the schema:
- `solver_status` / `solver_acceptable` / `kqp_pass` are ALWAYS recorded
  for every method (the verification pipeline runs in full per §4.1),
  even when the method does not feed them back to the agent. "skipped"
  is no longer a valid value for these fields — use the actual measured
  status.
- `success` follows the §4.2 conjunction (PipelineValid ∧ SolverValid ∧
  KQPSamplePass). `strict_success` is the secondary criterion.
- `repair_cost` follows the §4.6 formula
  (`Σ CED_declared + 0.1×n_execution + 0.1×n_verification`).

A `benchmark_summary.json` is also produced per method, aggregating all
samples' `result_schema` into the metric set defined in §5–7.

---

## 10. Artifact Save Protocol

For each `(method, sample_id)` pair, save:

```
experiments/results/<method>/<sample_id>/
  iter_<NN>/
    IR_t.json             ← input IR
    IR_t1.json            ← output IR
    ced.json              ← CED_declared, CED_executed, CED_text
    solver_feedback.json  ← Solver Feedback result (ALWAYS saved — the
                            verification pipeline runs in full per §4.1;
                            a method merely may not inject it into the
                            agent prompt, but the measured result is
                            always recorded for Success computation &
                            failure attribution)
    kqp_feedback.json     ← KQP Feedback result (ALWAYS saved; same note)
    generated_script.py
    generated.step
    adapter_report.json
    declared_trace.json
    executed_trace.json
    stdout.txt
    stderr.txt
    agent_request.json   ← LLM prompt + token counts
    agent_response.json  ← LLM response
    timing.json           ← per-stage wall-clock
  repair_summary.json
```

A top-level `experiments/reports/benchmark_<method>_summary.json` aggregates
all `(method, sample_id)` results into the metric set.

---

## 11. Acceptance

1. `doc/experiment_contract_v0.1.md` complete
2. `doc/frozen_components_for_repair_benchmark.md` complete
3. `experiments/config/benchmark_config_v0.1.json` complete
4. 4 methods (M0/M1/M2/M3) clearly defined
5. Main metrics defined and the metric base code is built
6. Result schema implemented
7. Files organized in `experiments/` directory tree (config/, results/, reports/)
8. CED implementation reused from `cad_edit_distance/`
9. Success criteria clearly stated
10. Artifact save protocol documented
11. Secondary analysis (§13 stop-bar sensitivity) protocol documented;
    it is post-hoc on M3 artifacts, gated, and does not block the main
    ablation.

---

## 12. Reproducibility rules

1. **No silent patches** during the experiment.  Any modification of
   frozen components requires a version bump and re-running the affected
   ablation.
2. **Same LLM** (ZHIPU glm-5.1), **same temperature** (0.0), **same
   max_iter** (3), **same input format** for all 4 methods.
3. **No tweaking** the prompt or metric to favor a particular method.
4. Each method runs in a **separate subprocess** to avoid LLM state
   leakage between methods.

---

## 13. Secondary Analysis — Stop-Bar Sensitivity (Threshold Effect)

### 13.1 Purpose & relationship to the main ablation

The main ablation (§3, M0–M3) fixes the stop bar and varies only the
feedback channels, isolating the *information value* of each feedback.
This §13 analysis answers a **different, complementary question** that
M0–M3 cannot:

> **RQ-T (threshold effect):** Does the *strictness of the stop bar
> itself* affect the final CAD quality — i.e., if a system stops as soon
> as a weaker bar is met, how much final quality (measured under the
> full bar) is lost to premature stopping / over-trust?

This is the deployment-oriented question: "a system that lacks solver
or KQP components, and therefore can only self-assess against a weaker
bar, how badly does it over-trust its own output?" M0–M3 does not
measure this, because all four methods stop at the same full bar.

### 13.2 Why a post-hoc analysis on the M3 trajectory (zero new LLM calls)

The threshold effect is captured **for free** from the M3 run's stored
per-iteration artifacts (§10). Rationale:

- The agent's repair decisions depend ONLY on the feedback it receives.
  M3 receives full feedback, so its trajectory is the "best-informed
  agent" reference. Re-running with weaker feedback (as a literal N0–N3)
  would reproduce ≈ M0/M1/M2 behavior and add little new signal about
  the *bar* itself.
- The only thing a weaker bar changes is **when S3 fires** (earlier),
  hence **how many iterations the agent actually gets** and **which
  intermediate CAD gets frozen as the final output**. Both are
  recoverable from M3's stored trajectory by post-hoc re-evaluation —
  no new LLM calls, no new agent runs.

Therefore this analysis is **deterministic post-processing** on frozen
M3 artifacts. It is scoped as secondary (not a main ablation table); it
informs the deployment narrative and, if the gap is large, motivates an
optional N0–N3 deployment study (§13.7).

### 13.3 Four candidate stop bars

Let the three component checks be:

```
P = PipelineValid(C)      (compile ∧ execute ∧ step_export ∧ occt_load)
S = SolverValid(C)        (solver.status ∈ {fully_constrained, under_constrained})
K = KQPSamplePass(C)      (all mandatory KQP queries pass)
```

Define four monotonically strengthening bars:

| Bar | Definition | Meaning |
|---|---|---|
| **B0** | P | "the code runs and exports a STEP" — weakest |
| **B1** | P ∧ S | "+ constraints are constructible" |
| **B2** | P ∧ K | "+ geometric intent is met" |
| **B3** | P ∧ S ∧ K | full bar (= the main ablation's S3) — strongest |

Monotonicity: B0 ⊆ B1 ⊆ B3 and B0 ⊆ B2 ⊆ B3 (B1 and B2 are
incomparable). This nesting is what makes cross-bar gaps interpretable.

### 13.4 Post-hoc replay protocol

For each M3 sample with stored trajectory
`C_{i,0} → C_{i,1} → C_{i,2} → C_{i,3}` (each C_{i,k} = the IR/STEP at
iteration k, with all component checks already recorded), replay under
each bar B ∈ {B0, B1, B2, B3}:

```
k*_B(i) = min{ k ∈ {0,1,2,3} : B(C_{i,k}) = True }      # first bar-meeting iter
        = ∞ if the bar is never met within the trajectory

stop_iter_B(i) = k*_B(i) if k*_B(i) < ∞
               else 3                                    # ran out of budget
```

The "frozen final CAD" under bar B for sample i is `C_{i, stop_iter_B(i)}`.
Note: this is the SAME physical CAD artifact M3 produced at that
iteration — we do NOT generate new CAD. We only change *which iteration's
CAD counts as the final answer*.

Then re-evaluate **every** bar-B-frozen final CAD under the **common
full bar B3**:

```
final_quality_B(i) = B3(C_{i, stop_iter_B(i)})           # uniform quality yardstick
```

`final_quality_B3` (B=B3) is trivially the main-ablation M3 Success@3.
`final_quality_B0` (B=B0) is the key new number: "if the system had
stopped as soon as the code ran, what fraction of outputs would still
pass the full bar?"

### 13.5 Reported metrics

For each bar B ∈ {B0, B1, B2, B3}, report on the M3 sample set:

| Metric | Definition |
|---|---|
| **own-bar stop rate** | fraction of samples where the bar is ever met within ≤3 iters, `1[ k*_B < ∞ ]` |
| **mean stop iter (own-bar)** | mean of `stop_iter_B(i)` over bar-meeting samples |
| **common-bar final quality** | `final_quality_B(i) = B3(C_{i,stop_iter_B(i)})` — THE cross-bar-comparable number |
| **quality gap vs B3** | `final_quality_B3 − final_quality_B` — how much full-bar quality is lost by stopping at a weaker bar |
| **token savings vs B3** | `tokens_used(M3 up to stop_iter_B3) − tokens_used(M3 up to stop_iter_B)` — efficiency gained by earlier stopping |

The **central table**:

| Stop bar | own-bar stop rate | mean stop iter | common-bar (B3) final quality | quality gap vs B3 | token savings vs B3 |
|---|---|---|---|---|---|
| B0 (P) | … | … | … | … | … |
| B1 (P∧S) | … | … | … | … | … |
| B2 (P∧K) | … | … | … | … | … |
| B3 (P∧S∧K) | … | … | (reference = M3 Success@3) | 0 | 0 |

**Only the `common-bar final quality` column is cross-bar comparable.**
The `own-bar stop rate` column is NOT comparable across bars (different
denominators) and must be labeled as such in the table caption.

### 13.6 Interpretation rules

- **If quality gap B0→B3 is small:** a system that stops at "code runs"
  loses little final quality — the bar strictness matters little for
  this dataset. This would be a reassuring deployment finding.
- **If quality gap B0→B3 is large:** weaker bars cause substantial
  over-trust — the verification components (solver, KQP) are essential
  not just as feedback but as *gates*. This motivates either always
  running the full bar, or motivates the optional N0–N3 deployment
  study (§13.7).
- **B1 vs B2 gap decomposition:** comparing how much quality each
  component *as a gate* (not as feedback) protects. This is distinct
  from M1/M2 which measure each component *as feedback*.
- **Honest disclosure:** this analysis uses the M3 (full-feedback)
  trajectory only. A weaker-bar *deployment* would also weaken the
  feedback, so real deployment quality ≤ the common-bar quality reported
  here. The numbers here are an **upper bound** on weaker-bar deployment
  quality. This caveat is mandatory in the writeup.

### 13.7 Optional follow-up: N0–N3 deployment study (conditional)

If §13.6 finds a **large** B0→B3 quality gap, an optional N0–N3 study
may be run to quantify real deployment behavior (weaker bar AND weaker
feedback simultaneously). N0–N3 are defined ONLY if triggered:

| Group | Pipeline runs | Solver runs | KQP runs | Feedback to agent | Stop bar (S3) |
|---|---|---|---|---|---|
| N0 | ✓ | ✗ | ✗ | pipeline only | P |
| N1 | ✓ | ✓ | ✗ | pipeline + solver | P ∧ S |
| N2 | ✓ | ✗ | ✓ | pipeline + KQP | P ∧ K |
| N3 | ✓ | ✓ | ✓ | pipeline + solver + KQP | P ∧ S ∧ K |

**Critical reporting rule if N0–N3 are run:** every group's final CAD is
ALSO re-evaluated under the common full bar B3, and BOTH columns are
reported:

- `own-bar success` (N0=P-rate … N3=full-rate) — NOT cross-group comparable
- `common-bar (B3) success` — cross-group comparable

The `own-bar − common-bar` gap per group = that deployment config's
over-trust magnitude. Without the common-bar column, N0–N3 numbers are
misleading (N0's high own-bar rate is just a low bar, not good quality).

**Decision gate:** N0–N3 are NOT run by default. They are triggered
only if (a) the §13.6 B0→B3 gap is large enough to warrant deployment
narrative, AND (b) the paper explicitly needs deployment-cost numbers.
Otherwise §13 alone suffices.

### 13.8 Artifact & reproducibility

- Input: frozen M3 per-iteration artifacts under
  `experiments/results/M3_*/<sample_id>/iter_<NN>/` (IR, STEP,
  solver_feedback.json, kqp_feedback.json — all already saved per §10).
- Output: `experiments/reports/threshold_sensitivity_analysis.json` and
  `experiments/reports/threshold_sensitivity_report.md`.
- The replay script is deterministic (no LLM, no randomness); same M3
  artifacts ⇒ identical numbers. Re-runnability is guaranteed.
- No new LLM tokens are consumed. No frozen components are modified.
- This analysis may be re-run any time after M3 completes; it does not
  block the main ablation.

### 13.9 Acceptance for §13

1. The four bars B0–B3 are defined with the monotonicity stated in §13.3.
2. The replay protocol (§13.4) reuses M3 stored artifacts only — no new
   agent/LLM runs.
3. The central table (§13.5) reports both own-bar (non-comparable) and
   common-bar (comparable) columns, with the caption labeling them as such.
4. The over-trust upper-bound caveat (§13.6) is included in any writeup.
5. N0–N3 (§13.7) are gated behind the §13.6 gap-size condition and are
   not part of the default experiment plan.