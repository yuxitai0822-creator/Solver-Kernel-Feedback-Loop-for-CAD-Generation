# B-009 Root-Cause Diagnosis Guide

> **Date**: 2026-07-17
> **Status**: READY FOR EXECUTION
> **Owner**: execution agent
> **Predecessor**: EX1/EX2 operators + eligibility filter done; B-009
>  frame-only attempt done (15/50 clean regressed)
> **Goal**: determine WHY 15 clean samples regress under frame-only KQP,
>  so we can fix KQP's bbox detection without masking or abandoning EX1/EX2.

---

## 0. Why this diagnosis matters (read first)

The execution agent's B-009 fix attempts concluded that EX1/EX2 are
"invisible to KQP because they only reorder the bbox SET." **This
conclusion is wrong.** The evidence already collected disproves it:

- Attempt 1 (frame-only) made EX 6/6 detectable. So EX1/EX2 ARE
  detectable under frame-axis projection.
- The reason the agent rolled back was that frame-only regressed 15/50
  clean samples. But that regression is NOT a flaw of frame-only — it
  is frame-only **exposing** an inconsistency that best-match was
  **masking**.

The 15 regressions mean: for those 15 clean samples, the body's actual
span along `Design_Plan.frame.u_dir` does not equal `expected_u`. This
has only two possible root causes:

- **(I) Direction mismatch**: the body's actual orientation differs
  from what `Design_Plan.frame` declares. E.g., DP says u→Z but the
  body's long edge is along X.
- **(II) Value misassignment**: the DP compiler put the right dimension
  into the wrong u/v/w slot. E.g., the body is oriented correctly, but
  `expected_u` holds the value that should be `expected_v`.

This guide determines which one it is. **Do not attempt to fix KQP,
DP compiler, or Reconstruction Engine until this diagnosis is complete.**
Fixing before diagnosing is how the agent ended up rolling back twice.

---

## 1. The wrong conclusion to avoid

The agent's report said:

> "EX1 is 'same SET reorder', doesn't change KQP expected matching, so
> KQP invisible. This is the fundamental assumption error of plan §2.1/§2.2."

This is incorrect because it conflates two different things:

- KQP `expected` values come from the **Design Plan** (not perturbed by EX1).
- KQP `frame` directions come from the **Design Plan** (not perturbed by EX1).
- EX1 perturbs the **history JSON** → changes the actual body orientation.

Under best-match: the runner picks whichever world-axis span is closest
to `expected`. Since EX1 only permutes the three spans, and the SET is
unchanged, best-match always finds a match → invisible. **Correct.**

Under frame-axis: the runner projects the body onto `frame.u_dir` (from
DP, unperturbed). After EX1 the body is reoriented, so its span along
the *original* `frame.u_dir` changes → no longer matches `expected` →
detected. **Also correct, and this is why attempt 1 got 6/6.**

So the agent's "fundamental assumption error" claim is itself the error.
EX1/EX2 are sound. The blocker is the 15 clean regressions, which is an
**independent DP/frame consistency bug** that best-match was hiding.

---

## 2. Inputs

- 50 clean samples: `Reconstruction_results/<sid>/generated.step` +
  `DesignPlan/compiler/instances_v6/<sid>.design_plan.json` +
  `kqp/outputs/compiler_v0.1/<sid>.kqp_instance.json`
- The frame-only KQP runner attempt (preserved at
  `kqp/runner/query_dispatcher.py.b009_frame_only` if the agent saved it;
  if not, reapply the frame-only patch from the B-009 attempt log).
- `experiments/pilot/verify_b009_fix.py` (the verification script the
  agent already wrote).

---

## 3. Step 1 — Identify the exact 15 regressing samples

Run frame-only KQP on all 50 clean samples. Record per-sample per-query
pass/fail. The 15 regressing samples are those with ≥1 failing query
under frame-only that passed under best-match.

Output: `experiments/b009_diagnosis/regressed_samples.json`

```json
{
  "n_clean": 50,
  "n_pass_bestmatch": 50,
  "n_pass_frameonly": 35,
  "n_regressed": 15,
  "regressed_samples": [
    {
      "sample_id": "...",
      "regressed_queries": [
        {"query_id": "q_bbox_u", "expected": 19.0, "frame_axis": "u",
         "frame_dir": [0,0,1], "frame_axis_span": 1.5875,
         "world_spans": {"x": 279.4, "y": 215.9, "z": 1.5875},
         "bestmatch_picked": "z", "bestmatch_span": 1.5875}
      ]
    }
  ]
}
```

For each regressed query, record:
- `expected` (from KQP instance)
- `frame_dir` (from Design Plan `solid_bodies[0].frame`)
- `frame_axis_span` (project clean STEP bbox onto frame_dir)
- `world_spans` (X/Y/Z spans of clean STEP)
- `bestmatch_picked` (which world axis best-match chose, and its span)

This single file is the evidence base for everything that follows.

---

## 4. Step 2 — Classify each regression as (I) or (II)

For each regressed query, apply this decision tree:

```
Let E = expected value
Let F = frame_axis_span (body projected onto DP's frame.u_dir)
Let W = {world spans} = {X, Y, Z spans of the clean STEP}

Question A: Does F ≈ E (within tolerance)?
  YES → the regression is NOT a direction mismatch on this query.
         The query should have passed under frame-only. If it's in the
         regressed list, re-check the projection math (possible bug in
         frame-axis implementation). → class (III) implementation bug.

  NO  → go to Question B.

Question B: Does some other world axis span W[axis] ≈ E?
  YES → the body HAS the expected dimension, just not along frame.u_dir.
        → class (I) direction mismatch: body orientation ≠ DP frame.
        Record WHICH world axis matches: this tells us the body's true
        orientation for this dimension.

  NO  → the expected value doesn't match ANY world span of the body.
        → class (II) value misassignment: DP compiler put the wrong
        number into expected, OR the body itself is wrong.
```

For each regressed sample, also cross-check all THREE bbox queries
(u/v/w), not just the failing one. A consistent (I) pattern looks like:
"u fails, but u's expected matches v's world span; v fails, but v's
expected matches u's world span" — a clean axis permutation. A (II)
pattern looks like: numbers don't line up across any permutation.

Output: `experiments/b009_diagnosis/regression_classification.json`

```json
{
  "class_I_direction_mismatch": [
    {"sample_id": "...", "n_queries": 2,
     "permutation": "u<->v",  // which axes are swapped
     "evidence": "expected_u=19.0 matches world Y; frame.u_dir=[0,0,1] points to Z"}
  ],
  "class_II_value_misassignment": [
    {"sample_id": "...", "n_queries": 1,
     "evidence": "expected_u=19.0 matches no world span; spans are {80,50,20}"}
  ],
  "class_III_impl_bug": [
    {"sample_id": "...", "evidence": "frame_axis_span=19.0 ≈ expected=19.0 but query failed"}
  ]
}
```

---

## 5. Step 3 — If class (I) dominates, trace where the direction mismatch originates

Class (I) means: body's actual orientation ≠ DP's declared frame. Three
sub-hypotheses, each testable from existing artifacts:

### (I-a) DP compiler extracts frame wrong from history

Check: does `Design_Plan.frame.u_dir` match the history's
`Sketch.reference_plane.normal` / `transform`?

For each class-(I) sample:
- Read `Reconstruction_results/<sid>/input_history.json`
- Find the Sketch entity's `reference_plane.plane.normal` and
  `transform.x_axis`/`y_axis`.
- Compare to `DesignPlan/.../<sid>.design_plan.json`'s `frame.u_dir`/`v_dir`/`w_dir`.
- If they disagree → DP compiler bug in frame extraction.

### (I-b) Reconstruction Engine builds STEP in wrong orientation

Check: does the clean STEP's actual orientation match the history's
declared plane?

For each class-(I) sample:
- The history says the sketch is on plane XZ (normal≈[0,1,0]).
- The clean STEP's bbox should reflect extrusion along Y.
- If the STEP's extrusion axis is actually Z (not Y) → executor bug:
  it ignored the sketch plane and used default XY. **This is the
  real B-008** — the one the agent prematurely closed as "not a bug."

### (I-c) KQP frame injection drops corrective_transform

Check: does the Design Plan have a `corrective_transform` field that
`run_kqp.py` ignores?

The `query_dispatcher.py` L48 comment already says: "frame labels may
be unreliable (corrective_transform issue)." If DP has a
`corrective_transform` and run_kqp doesn't apply it, frame_dir is
pre-transform → points to wrong world axis → class (I).

Output: `experiments/b009_diagnosis/class_I_subclassification.json`

```json
{
  "I_a_dp_compiler": ["sample_id_1", ...],
  "I_b_executor": ["sample_id_2", ...],
  "I_c_transform_drop": ["sample_id_3", ...],
  "unclear": ["sample_id_4", ...]
}
```

---

## 6. Step 4 — If class (II) appears, audit the DP compiler's bbox extraction

Class (II) means expected values are wrong regardless of direction. For
each class-(II) sample:
- Read the history's actual extrude distance + profile dimensions.
- Read the DP's `bbox.u/v/w` expected values.
- Check if the DP compiler assigned a dimension to the wrong slot
  (e.g., put extrude distance into `u` instead of `w`).

This is a DP compiler bug, fixable independently of KQP.

---

## 7. Step 5 — Synthesize and recommend

Write `experiments/b009_diagnosis/diagnosis_report.md` with:

1. **Headline finding**: of the 15 regressions, how many are (I) vs (II)
   vs (III)?
2. **If (I) dominates**: which sub-class (I-a/I-b/I-c)? This tells us
   whether to fix DP compiler, Reconstruction Engine, or KQP frame
   injection.
3. **Expected fix scope**: which frozen component needs modification,
   and whether the fix is localized (one function) or systemic.
4. **Prediction for EX1/EX2**: after the recommended fix, will frame-only
   KQP pass all 50 clean AND detect all 6 EX? If yes, EX1/EX2 are
   unblocked. If no, what's the residual problem?
5. **Do NOT fix anything in this step.** This is diagnosis only. The
   report ends with a recommendation; the user decides whether to
   authorize the fix.

---

## 8. Acceptance criteria for the diagnosis

1. `regressed_samples.json` lists exactly the 15 regressing samples with
   per-query evidence (§3).
2. Every regressed query is classified (I)/(II)/(III) with explicit
   evidence (§4).
3. If (I) appears, every class-(I) sample is sub-classified (I-a/I-b/I-c)
   with evidence from history vs DP vs STEP (§5).
4. `diagnosis_report.md` states the headline finding and a fix
   recommendation, but **makes no code changes**.
5. The report explicitly answers: "After the recommended fix, will
   frame-only pass 50 clean + detect 6 EX?"

---

## 9. What not to do

1. **Do not fix KQP, DP compiler, or Reconstruction Engine during this
   diagnosis.** Diagnosis only. The agent has twice jumped to "fix"
   before understanding, producing rollbacks. This step is read-only
   analysis of existing artifacts.
2. **Do not re-run the full pilot.** This diagnosis works on clean
   samples + EX negatives only; no LLM calls needed.
3. **Do not conclude "EX1/EX2 are fundamentally invisible."** That
   conclusion is already disproven by attempt 1 (6/6 EX detected under
   frame-only). The task is to explain the 15 clean regressions, not to
   re-litigate EX visibility.
4. **Do not modify frozen files.** If a frozen file needs reading,
   read it. The `_v0.1_FROZEN.py` backups are for reference; do not
   touch the live files until the user authorizes a fix.
5. **Do not skip the (III) class.** If any regressed query has
   `frame_axis_span ≈ expected` but still failed, the frame-axis
   implementation itself has a bug — this must be caught before
   blaming DP or executor.

---

## 10. Hand-off note

The agent's B-009 work was not wasted: it produced the key finding
(frame-only makes EX 6/6 detectable) and the key obstacle (15 clean
regressions). This diagnosis converts that obstacle from a "reason to
give up" into a "specific bug to locate." The most likely outcome is
(I-b) executor ignoring sketch plane for some samples — which would
mean the real B-008 was prematurely closed and needs reopening. Be
prepared for that.

Deliver the diagnosis report; the user will decide the fix based on it.
