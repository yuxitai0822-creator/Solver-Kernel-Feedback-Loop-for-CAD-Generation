# Phase 2A + 2B Execution Guide

> **Date**: 2026-07-22
> **Status**: READY FOR EXECUTION (Phase 2A); Phase 2B gated on B-009 diagnosis
> **Owner**: execution agent
> **Replaces**: original proposal Tasks 1–6
> **Relationship to original proposal**:
>   - Original Task 1 (IR-free generation) → Phase 2A Task A1
>   - Original Task 2 (Code2Oper parser)   → Phase 2A Task A2
>   - Original Task 3 Level 1 (derived query) → **DROPPED** (proven not to break B-007; volume errors stem from DP-visible params)
>   - Original Task 3 Level 2 (relational) + Task 4 (LLM Verification Agent) → **DEFERRED to Phase 2C** (independent arm)
>   - Original Task 5 (hard negatives) → Phase 2B Task B2 (Type A + EX1/EX2 only)
>   - Original Task 6 (new pilot) → Phase 2B Task B3

---

## 0. Why this guide supersedes the original Tasks 1–6

Two corrections from the two-round discussion:

1. **Level 1 derived query (volume/surface_area) does NOT break B-007.**
   A volume error's root cause is a DP-visible parameter (extrude distance).
   M0 reads `extrude(15)` vs DP `h=20` and self-corrects without needing
   volume. Derived queries only break B-007 when the error source is NOT
   a DP-visible parameter — which means direction/position/topology errors,
   not parameter errors. So derived queries are dropped from the B-007 path;
   the real B-007 fix is the frame-aware bbox detection (B-009).

2. **Task 4 (LLM Verification Agent) is deferred, not killed.**
   It introduces a second uncontrolled LLM variance source into the main
   ablation, blurring RQ1 attribution. But it IS the long-term answer to
   compiler scalability (compiler is rule-level, doesn't scale to
   fillet/pattern/assembly/relational queries). So it becomes Phase 2C,
   an independent arm (KQP-LLM) reported alongside deterministic KQP
   (KQP-det), with its own RQ (LLM-verification vs deterministic-verification
   incremental value). Phase 2A/2B keep deterministic KQP as the controlled
   ruler.

KQP scalability assessment that grounds this split:
- **KQP runner** (STEP → query result via OCCT): scales well — geometry-level
  queries (volume/bbox/centroid) work on any solid regardless of how it was
  built.
- **KQP compiler** (DP → query instance): scales poorly — each feature type
  needs a new rule. This is the real bottleneck, but it only bites when
  Type B/C/D negatives (relational/topology/constraint) are introduced,
  which is Phase 2C territory.

For Phase 2A/2B (parameter + direction errors), the deterministic compiler
is sufficient. Forcing Task 4 in now would pay the variance cost without
the feature coverage that justifies them.

---

# PHASE 2A — Scale Fix on the Generation Side

**Goal**: free the generation pipeline from the CAD IR schema lock, so new
operation types / longer scripts / more complex CAD don't require IR-compiler
adaptation. CED remains computable via a post-hoc parser.

**Does NOT touch**: KQP (compiler or runner), Design Plan, perturbation
battery, the B-009 frame issue. Deterministic KQP stays as the controlled ruler.

**RQ answered by 2A**: none directly — this is infrastructure. It unblocks
Phase 2B by allowing harder negatives (which need richer CAD scripts) to
flow through generation.

---

## Task A1 — IR-Free Generation Pipeline

### A1.1 Background

Current generation path is locked by CAD IR:
```
Design Plan → CAD IR compiler → CAD IR → IR Adaptor → CAD Script → Execution → STEP
```
Every new operation type requires: IR schema + history2IR compiler + adaptor.
This is the scale blocker on the generation side.

### A1.2 New generation path

```
Design Plan → LLM CAD Agent → cadquery script → Execution → STEP
```

The LLM CAD Agent directly produces cadquery (or FreeCAD) Python. It owns:
- API selection
- modeling strategy
- operation ordering
- parameter values

No IR, no adaptor in the generation path.

### A1.3 What to retain (do NOT delete)

- **CAD IR schema, history2IR compiler, IR Adaptor**: keep frozen. They
  are NOT deleted. They are repositioned as *optional* tools for:
  - controlled editing experiments (if you ever want to constrain the agent)
  - behavioral-equivalence cross-checks
  - legacy reproduction of the v0.1 pipeline
- **Reconstruction Engine**: keep as the GT-reconstruction oracle (still
  needed for perturbation negative generation in Phase 2B).

### A1.4 Implementation

**A1.4.1 — LLM CAD Agent module**

New module: `cad_agent/` (sibling to `cad_repair_loop/`)
```
cad_agent/
  agent.py            ← LLM call: Design Plan → cadquery script
  prompt_builder.py   ← builds the generation prompt
  schema.py           ← output contract (script + metadata)
```

Agent input: Design Plan JSON.
Agent output (strict JSON contract):
```json
{
  "script": "<cadquery python source>",
  "operations_declared": ["extrude", "circle", ...],
  "notes": "..."
}
```

The agent MUST output executable cadquery. It MUST NOT output IR. It MAY
include comments. The script must run under the existing CADQUERY_PYTHON
env (`D:/Anaconda/envs/cad_subproject1/python.exe`).

**A1.4.2 — Unified CAD execution wrapper**

New module: `cad_runtime/executor.py`
```python
def execute_cad_script(script: str, out_dir: Path) -> dict:
    """Run a cadquery script, export STEP, return pipeline status."""
    # returns:
    # {
    #   "compile_status": bool,       # script parses
    #   "execution_status": bool,     # runs without exception
    #   "step_export": bool,          # STEP file produced, size>0
    #   "occt_load": bool,            # OCP can read the STEP
    #   "runtime_error": str | None,
    #   "step_path": Path | None,
    #   "stdout": str, "stderr": str
    # }
```

This wrapper replaces the IR-adaptor subprocess. It is IR-agnostic: it
takes a script, runs it, exports STEP. The repair loop will call this
instead of `_run_adaptor(ir, ...)`.

**A1.4.3 — Wire into the repair loop**

Modify `run_benchmark_v0.2.py` (or a new `run_benchmark_v0.3.py` — see
A1.5) so that:
- Stage 1 (Adaptor) is replaced by `execute_cad_script`
- The agent receives the current script (not IR) as `[CURRENT CAD]`
- The agent outputs a revised script (not IR repair operations)
- S2 (no-change) is now: `script_{t+1} == script_t` (string compare after
  normalization: strip comments/whitespace)

The four methods M0–M3 and the S1–S4 stop rules are unchanged in spirit;
only the representation under repair changes (script vs IR).

### A1.5 Frozen-file rule

`run_benchmark_v0.2.py` is the frozen v0.2. **Do NOT modify it in place.**
Back it up to `run_benchmark_v0.2_FROZEN.py`, then create
`run_benchmark_v0.3.py` for the IR-free path. v0.2 stays runnable for
legacy reproduction. Same rule applies to any other frozen file touched.

### A1.6 Acceptance

1. LLM CAD Agent produces a cadquery script from a Design Plan (no IR
   involved in generation).
2. `execute_cad_script` runs the script and produces a STEP on at least
   90% of the 46 clean Design Plans (sanity check — the agent should be
   able to reproduce simple extrude-from-sketch parts).
3. The repair loop runs end-to-end on the IR-free path for all 4 methods.
4. v0.2 frozen file is intact and still runnable.
5. No KQP file is modified in this task.

---

## Task A2 — Code2Operation Parser + CED Adapter

### A2.1 Background

With IR gone from generation, CED_declared (operation-level edit distance)
loses its input. Solution: a deterministic post-hoc parser that converts
cadquery script → structured operation representation, feeding the existing
CED computation. Crucially, this parser:
- does NOT participate in generation
- does NOT constrain the LLM's output style
- does NOT need to handle 100% of scripts (CED_text is the fallback)

### A2.2 Operation taxonomy (Phase 2A scope)

Cover only what the sanity set + expected Phase 2B negatives use:

- Sketch/Profile: line, circle, arc, rectangle, polygon
- Feature: extrude, cut, union, shell, fillet
- Transform: translate, rotate, mirror

Each operation declares:
```json
{
  "operation": "extrude",
  "parameters": {"distance": 20.0, "direction": [0,0,1], "profile": "sketch_0"},
  "source": {"api": "cq.Workplane.extrude", "argument": "distance"}
}
```

### A2.3 Parser technology

NOT simple regex. Use Python AST:
```
cadquery script
  → ast.parse
  → walk ast, extract cadquery API calls (attribute access chains like
    wp.rect(...).extrude(...))
  → semantic mapping (api call → operation type + parameter extraction)
  → operation graph (ordered list of operations with dependencies)
```

Example:
- Input: `result = cq.Workplane("XY").rect(80, 50).extrude(20)`
- Output:
  ```json
  [
    {"operation": "rectangle", "parameters": {"width": 80, "height": 50}, "source": {"api": "rect"}},
    {"operation": "extrude", "parameters": {"distance": 20}, "source": {"api": "extrude"}}
  ]
  ```

### A2.4 CED adapter (CRITICAL — incorporates the agreed fallback rule)

Adapt the existing `cad_edit_distance/compute_ced.py` to accept parsed
operation lists instead of IR. The metric-selection rule becomes:

```
For a pair (script_t, script_{t+1}):
  parse both → op_t, op_{t+1}
  if both parse successfully:
    CED_declared = weighted_op_edit_distance(op_t, op_{t+1}) / norm_base
    CED_text     = normalized_levenshtein(script_t, script_{t+1})   # auxiliary
  else:
    CED_declared = None  # NOT computable
    CED_text     = normalized_levenshtein(script_t, script_{t+1})   # PRIMARY fallback
```

**Acceptance rule (corrected per discussion)**: do NOT require "≥95% must
parse". Instead:
- Report `parse_coverage = (# scripts parseable) / (# scripts total)`
- For parseable pairs: report CED_declared
- For unparseable pairs: fallback to CED_text, flag the pair
- The metric selection table in the contract §6.6 already supports this
  (CED_text is the documented fallback) — do NOT drop it.

### A2.5 Implementation

New module: `code2oper/`
```
code2oper/
  taxonomy.py         ← operation definitions + parameter schemas
  ast_parser.py       ← cadquery script → AST → API call extraction
  semantic_mapper.py  ← API calls → operation graph
  parse.py            ← entry: script → operation list (or None on failure)
  tests/
    test_parse_clean.py        ← parse the 46 reconstructed scripts
    test_parse_llm_output.py   ← parse LLM-generated scripts (once A1 runs)
  reports/
    parse_coverage.json
```

### A2.6 Acceptance

1. Parser runs on the 46 reconstruction-engine-generated scripts (these
   are deterministic, known-good cadquery). Report parse coverage.
2. Parser runs on ≥20 LLM-generated scripts from A1's sanity run. Report
   parse coverage. Expect lower than (1) — that's fine, CED_text catches
   the rest.
3. CED_declared is computable on parseable pairs; CED_text is computed
   on all pairs as fallback.
4. A side-by-side CED report on 5 manual edit pairs (e.g., change a
   distance, add a fillet, swap two ops) shows CED_declared tracks the
   intended edit magnitude.
5. `parse_coverage.json` reports both clean-script and LLM-script coverage
   separately.

---

## Phase 2A acceptance summary

| Item | Criterion |
|---|---|
| Generation path | Design Plan → LLM → cadquery script → STEP, no IR in path |
| Execution wrapper | `execute_cad_script` runs scripts, exports STEP, returns pipeline status |
| Frozen files | v0.2 backed up; v0.3 created; v0.2 still runnable |
| Code2Oper parser | AST-based; reports coverage; does NOT require 95% |
| CED | CED_declared on parseable pairs, CED_text fallback on rest |
| KQP | UNTOUCHED in Phase 2A |

**Do NOT proceed to Phase 2B until 2A passes.** Phase 2B's harder negatives
need the IR-free generation path to flow through.

---

# PHASE 2B — Make the Ablation Show a Difference (Solve B-007)

**Goal**: under conditions where parameter errors are LLM-self-checkable
but direction errors are not, demonstrate M0 < M2. This is the first
honest test of RQ1.

**Core mechanism**: NOT derived queries (proven ineffective). It is the
**frame-aware bbox detection** (B-009 fix) that makes EX1/EX2 (direction
perturbations) KQP-detectable. Direction errors are not DP-self-checkable
(DP has no axis assignment), so M0's prior fails and KQP's execution-level
verification has leverage.

**Prerequisite (hard gate)**: the B-009 diagnosis guide
(`doc/b009_diagnosis_guide.md`) must be complete, and the 15 clean
regressions must be root-caused. If the root cause is fixable (likely
executor or DP-compiler bug), the fix must land and 50/50 clean must
pass under frame-only before Phase 2B proceeds.

---

## Task B1 — Frame-Aware KQP Bbox Detection (the B-009 fix)

### B1.1 What this task is

This is the B-009 fix, executed AFTER the diagnosis guide produces its
report. The diagnosis determines which sub-component to fix:
- (I-a) DP compiler frame extraction wrong → fix `DesignPlan/compiler/`
- (I-b) Reconstruction Engine executor direction wrong → fix
  `reconstruction_engine/executor.py` (the prematurely-closed B-008,
  likely the real culprit)
- (I-c) KQP frame injection drops corrective_transform → fix
  `kqp/runner/run_kqp.py` frame loading

And separately, the KQP dispatcher itself:
- Replace best-match bbox strategy with frame-axis projection in
  `kqp/runner/query_dispatcher.py` (the L60-83 best-match block).

### B1.2 Frozen-file rule

`query_dispatcher.py`, `executor.py`, `compiler.py` are frozen. Back each
up to `*_v0.1_FROZEN.py` (executor/compiler backups already exist from
the B-008 work — verify they're current). Create v0.2 versions for the
fixes. Do NOT overwrite frozen files.

### B1.3 Implementation steps

1. Wait for / consume the B-009 diagnosis report
   (`experiments/b009_diagnosis/diagnosis_report.md`).
2. Apply the recommended fix per the report's subclassification.
3. Switch `query_dispatcher.py` bbox_size branch from best-match to
   frame-axis projection (the attempt-1 logic that got EX 6/6).
4. Re-verify: 50/50 clean pass under frame-only. If the diagnosis-driven
   fix was correct, the 15 regressions should now pass too. If any still
   regress, isolate them (per the task5 isolation pattern) rather than
   mask with best-match.
5. Re-verify EX1/EX2: 6/6 detectable under frame-only.

### B1.4 Acceptance

1. 50/50 clean samples pass KQP under frame-only (or isolated set
   documented for any residual failures, with root cause).
2. EX1/EX2 6/6 detectable.
3. Frozen v0.1 files intact; v0.2 fix files created.
4. Diagnosis report filed; fix matches the report's recommendation.

---

## Task B2 — Hard Negatives (Type A + EX1/EX2 only) + Difficulty Pre-Validation

### B2.1 Scope restriction (important)

Phase 2B hard negatives cover ONLY:
- **Type A (parameter)**: existing E1–E6 battery (already built). LLM
  self-checkable — expected M0 ≈ M2 here. Kept as the "self-checkable
  control" stratum.
- **EX1/EX2 (direction)**: plane swap + coordinate flip. NOT LLM
  self-checkable (DP has no axis assignment) — expected M0 ≪ M2 here.
  This is the stratum that tests RQ1.

**Explicitly OUT of scope for 2B** (deferred to 2C):
- Type B (relational: hole-pair symmetry) — needs new query type
- Type C (topology: through vs blind hole) — needs new query type
- Type D (constraint missing) — needs solver-level query

These need the LLM Verification Agent (Task 4) and are bundled with it
in Phase 2C. Forcing them in 2B would either need deterministic-compiler
rules that don't scale (the original problem) or premature LLM-KQP
(variance contamination). Both are wrong for 2B.

### B2.2 EX1/EX2 finalization

The EX1/EX2 operators and eligibility filter already exist
(`task5_negative_perturbation/perturbation/operators_ex.py`,
`sampler_ex.py`). After B1 lands (frame-aware KQP works), regenerate EX
negatives through the full pipeline:
1. perturbed history → Reconstruction Engine → STEP
2. perturbed history → history2IR → IR (for legacy cross-check only)
3. STEP → frame-aware KQP → must fail expected bbox queries
4. Behavioral equivalence: KQP(history-rebuild) ≡ KQP(IR-execution)

Eligibility filter (already in sampler_ex.py): reject near-square /
near-cubic samples where the swap is invisible. Target ≥ 40 EX
negatives (EX1 + EX2 combined) after eligibility.

### B2.3 Difficulty pre-validation (CRITICAL — agreed point)

Before running M0–M3, run **M0 only** on ALL negatives (Type A + EX).
This is the difficulty-label empirical check:

For each negative, record whether M0 (no feedback, just Design Plan
self-check) repairs it within max_iter.

- If a "Hard" (EX) sample is repaired by M0 → it is NOT actually hard
  for this LLM. Re-label or drop. (The difficulty label must be
  empirically grounded, not assumed.)
- If an "Easy" (Type A) sample is NOT repaired by M0 → it is harder
  than assumed. Investigate (could be a pipeline bug, not genuine
  difficulty).

This pre-validation is what prevents the experiment from being
self-fulfilling (constructing "hard" data then declaring it hard). It
costs nothing extra — M0 runs anyway in the main ablation. Just run it
FIRST and analyze before M1/M2/M3.

Output: `experiments/prevalidation/difficulty_empirical_check.json`
```json
{
  "type_A": {"n": 104, "m0_repaired": 70, "rate": 0.67},
  "EX":     {"n": 40,  "m0_repaired": 5,  "rate": 0.12},
  "verdict": "EX is empirically harder than Type A (12% vs 67%) — labels hold"
}
```

**Gate**: if EX m0_repaired rate ≥ Type A rate, the difficulty labels
are inverted — STOP and re-examine before M1/M2/M3. Don't run a main
ablation on inverted labels.

### B2.4 Acceptance

1. ≥ 40 EX negatives pass behavioral equivalence and KQP detection
   (frame-aware, post-B1).
2. M0 pre-validation runs on all negatives; difficulty_empirical_check.json
   produced.
3. EX m0_repaired rate < Type A m0_repaired rate (labels empirically
   hold). If not, stop and escalate.

---

## Task B3 — New Pilot (M0–M3 on Type A + EX)

### B3.1 Design

- Sample set: 30 negatives, stratified:
  - 15 Type A (parameter, expected M0 ≈ M2)
  - 15 EX (direction, expected M0 ≪ M2)
- Methods: M0, M1, M2, M3 (unchanged from contract §3)
- max_iter: 3 (unchanged)
- All on the IR-free generation path (Phase 2A) + frame-aware KQP (B1)

### B3.2 Success criterion (NOT a success-rate chase)

The pilot is GO if:
- On Type A stratum: M0 ≈ M2 (within McNemar noise) — confirms the
  "LLM self-check handles parameter errors" finding.
- On EX stratum: M0 < M2 with the gap in the expected direction. With
  n=15 per stratum, McNemar needs ~40pp to detect significance; the
  pilot mainly checks the gap DIRECTION and rough magnitude, not p-values.

This is the first honest test of RQ1. If M0 ≈ M2 even on EX (after B1
+ B2), then either:
- the LLM prior is stronger than expected across the board → RQ needs
  reframing (escalate, do NOT silently expand samples)
- there's still a hidden information leakage (Design Plan somewhere
  encodes direction) → audit and fix

### B3.3 Acceptance

1. All 4 methods run on all 30 samples; run_result.json complete.
2. Per-stratum M0 vs M2 comparison reported.
3. If EX stratum shows M0 < M2: GO for full benchmark (104 Type A + ~40
   EX, all 4 methods).
4. If EX stratum shows M0 ≈ M2: STOP, escalate to user. Do NOT proceed
   to full benchmark — that would burn tokens on a known-null result.

---

## Phase 2B acceptance summary

| Item | Criterion |
|---|---|
| B-009 diagnosis | Complete; root cause identified |
| B1 frame-aware KQP | 50/50 clean pass + 6/6 EX detectable |
| B2 EX negatives | ≥40 pass behavioral equivalence + detection |
| B2 difficulty pre-validation | EX m0_rate < Type A m0_rate (labels hold) |
| B3 pilot | EX stratum shows M0 < M2 (direction, not necessarily p-significant) |
| Frozen files | All v0.1 backed up; v0.2 fix files created; v0.1 still runnable |

---

# Cross-Phase Rules (apply to both 2A and 2B)

## R1 — Frozen-file discipline
Any frozen file (`run_benchmark_v0.2.py`, `query_dispatcher.py`,
`executor.py`, `compiler.py`, `compute_ced.py`, etc.) MUST be backed up
to `*_FROZEN.<ext>` before modification. New logic goes in a versioned
file (`*_v0.3.py` / `*_v0.2.py` as appropriate). Original frozen files
stay runnable for legacy reproduction.

## R2 — Deterministic KQP is the controlled ruler
Phase 2A/2B do NOT replace KQP compiler/runner with an LLM. The
deterministic KQP is what makes M2-vs-M0 attribution clean (one variance
source: the generation LLM). LLM-based verification is Phase 2C, as a
separate arm.

## R3 — CED_text fallback is mandatory
Wherever CED_declared is computed (post-2A: from Code2Oper parse), the
CED_text fallback MUST be preserved and reported. Do NOT require 100%
parse coverage. Report parse_coverage alongside CED results.

## R4 — Difficulty labels are empirical, not assumed
Before any M0–M3 comparison, run M0 alone and verify the "hard" stratum
is empirically harder than the "easy" stratum. If labels are inverted,
stop. (Applies to Phase 2B; will apply again in 2C for Type B/C/D.)

## R5 — Escalate null results, don't amplify them
If a pilot shows M0 ≈ M2 on the stratum expected to show M0 < M2, STOP
and escalate. Do NOT silently expand the sample size hoping the gap
appears. A null result on a clean design is a finding; a null result on
a contaminated design is a waste.

## R6 — One RQ per phase
- Phase 2A: infrastructure (no RQ)
- Phase 2B: RQ1 (does KQP beat DP-self-check when self-check fails?)
- Phase 2C (future): RQ-LLM-KQP (does LLM verification beat deterministic
  verification, at what variance cost?)

Do NOT blend these. In particular, do NOT introduce LLM Verification
Agent into Phase 2B's main ablation.

---

# Execution order

```
Phase 2A:
  A1 (IR-free generation) → A2 (Code2Oper + CED adapter)
  Gate: 2A acceptance

Phase 2B (parallel track, gated on B-009 diagnosis):
  B-009 diagnosis (already in flight) → B1 (frame-aware KQP fix)
  B2 (EX negatives + difficulty pre-validation)  [needs A1 + B1]
  B3 (new pilot: M0–M3 on Type A + EX)           [needs A1 + B2]

Phase 2C (future, NOT in this guide):
  Task 3 Level 2 + Task 4 (LLM Verification Agent) as independent arm
  Type B/C/D hard negatives
  RQ: LLM-verification vs deterministic-verification incremental value
```

A1 and the B-009 diagnosis can proceed in parallel — they touch
different subsystems. A2 depends on A1 (needs LLM-generated scripts to
test the parser). B2 depends on both A1 (IR-free path) and B1 (frame-aware
KQP). B3 depends on B2.

---

# What to report back

After Phase 2A:
- `cad_agent/`, `cad_runtime/`, `code2oper/` modules created
- `run_benchmark_v0.3.py` created; v0.2 backed up
- 46-clean sanity run on IR-free path: STEP export success rate
- `parse_coverage.json`: clean-script and LLM-script coverage
- Side-by-side CED on 5 manual edit pairs

After Phase 2B:
- B-009 diagnosis report (already in flight, separate guide)
- B1 fix: 50/50 clean + 6/6 EX verification
- B2: ≥40 EX negatives + difficulty_empirical_check.json
- B3: pilot results, per-stratum M0 vs M2, GO/NO-GO decision
