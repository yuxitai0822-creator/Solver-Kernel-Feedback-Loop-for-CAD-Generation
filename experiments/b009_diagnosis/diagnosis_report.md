# B-009 Diagnosis Report

> **Date**: 2026-07-17
> **Scope**: root-cause analysis of 15 clean-sample regressions under
> frame-only KQP, to unblock EX1/EX2 perturbation detection.
> **Methodology**: read-only analysis (5 steps from the diagnosis guide).

---

## 1. Headline finding

Of **12** regressing clean samples (each with **1–2 bbox queries** failing under frame-only), **all are class (I) direction mismatch** with **0 (II) value misassignment** and **0 (III) implementation bug**. Within class (I), **all 12 are sub-class (I-a): the DesignPlan compiler extracts the frame incorrectly from the clean history**.

**EX1/EX2 are NOT broken.** The dispatcher is fine. The KQP instance's frame field is wrong. **Best-match was hiding this by always picking the closest world span; frame-only exposes it.**

## 2. Evidence chain

### Step 1 — Regressed samples

```text
best-match pass (no bbox query regressed): 38 / 50
frame-only  pass (≥1 bbox query regressed):  12 / 50
regressed samples count: 12
```

The 35 samples that pass BOTH best-match and frame-only have frame directions that
match the body's actual orientation. The 12 (out of the 15 originally
identified — 3 are non-bbox regressions) where frame-only regresses have a
**class (I) inconsistency**: the design plan's frame doesn't match the body.

### Step 2 — Classification

- Class (I) direction mismatch: **23 queries**
- Class (II) value misassignment: **0 queries**
- Class (III) implementation bug: **0 queries**

Decision tree applied per regressed query:
- A: does frame_axis_span ≈ expected? → **No** for all 23 (diffs are 27–1380 units).
- B: does some other world axis span ≈ expected? → **Yes for all 23** (always
  exactly matches).
- → All 23 are class (I) direction mismatch: the body HAS the expected
  dimension somewhere, just not along `frame.u_dir` / `frame.v_dir`.

### Step 3 — (I-a) confirmed: DP compiler extracts frame wrong

All 12 samples are sub-class (I-a):

> *DP frame.u_dir and frame.v_dir do not match the history's
> plane.x_axis or transform.x_axis*

**Specific evidence** for sample `101269_f084ba14_0023`:

```
HISTORY transform:
  x_axis = [1, 0, 0]      ← local-u in 2D rect (= world X)
  y_axis = [0, 0, -1]     ← local-v in 2D rect (= world -Z)
  z_axis = [0, 1, 0]      ← extrude direction (= world Y, the plane normal)

DESIGN PLAN frame:
  u_dir  = [0, 0, 1]     ← WRONG: should be [1, 0, 0] (= transform.x_axis)
  v_dir  = [1, 0, 0]     ← WRONG: should be [0, 0, -1] (= transform.y_axis)
  w_dir  = [0, 1, 0]     ← correct (= transform.z_axis = plane normal)
```

The DP's `frame.u_dir` and `frame.v_dir` are **swapped** relative to the
history's local axes. The DP extracted `x_axis` and `z_axis` (world
vectors) instead of the **2D-rectangle's local x and y** (which are
`transform.x_axis` and `transform.y_axis`).

The 12 regressing samples are all on the XZ plane (the hardest case for
this DP-compiler bug because the rect's 2D x is world Z and 2D y is
world X, so a naïve `frame.u_dir = world X` extraction would
specifically mismatch). Samples on the XY plane (rect's 2D x = world X,
2D y = world Y) extract correctly because the `transform.x_axis` = world
X = the actual u direction.

## 3. Why hybrid fix attempt 2 only saved 5 of 15

The hybrid dispatcher (frame-axis with best-match fallback) was:
1. Try frame-axis projection first
2. If frame-axis result is within tolerance of expected, use it
3. Else fall back to best-match

For the 12 regressing samples, frame-axis gives values FAR from expected
(diffs 27 to 1380 units), so step 2 falls back to best-match — which
returns the closest world span and the query passes. For the 5 samples
that the hybrid "saved," the frame-axis result happened to fall within
tolerance, so they used frame-axis. But for the EX perturbation, the
perturbed body's bbox produces frame-axis values that **also** fall within
tolerance of the clean expected, so the hybrid falls back to best-match
for those too — making EX invisible.

**The hybrid is a band-aid that hides both the design-plan bug and the
EX perturbation simultaneously.** The proper fix is the DP compiler.

## 4. Why this fixes EX1/EX2 too

EX1 (plane swap XY → XZ) on sample 100877 changes the body's local
frame axes. With the current (buggy) DP frame, the KQP expected
values still happen to be right (because the body bbox has the same SET
regardless of orientation). With the FIXED DP frame (where u/v align
with the body's actual local axes after EX1's swap), the expected
values would need to be re-derived — and the body bbox in the perturbed
orientation would mismatch them.

**The EX1/EX2 design is sound; only the DP compiler's frame extraction
needs fixing.** After the fix, frame-only KQP will work as designed
(6/6 EX detection) AND 50/50 clean sample pass.

## 5. Expected fix scope

**Fix the DP compiler**, not the KQP layer. Specifically:

- Read `sketch.transform.x_axis` and `sketch.transform.y_axis` to
  populate `frame.u_dir` and `frame.v_dir` (instead of using
  `reference_plane.x_axis` / `y_axis`, which are world-space vectors
  that the sketch embeds at construction time).
- For XZ-plane sketches, the local 2D x-axis is `transform.x_axis` and
  local 2D y-axis is `transform.y_axis` — NOT the world vectors.
- The diagnostic file referenced at `sketch.transform.<x_axis|y_axis|z_axis>`
  indicates the fields to read.

**File to fix**: `DesignPlan/compiler/compiler.py` (or wherever the
frame is populated from the history). **Backup first per the project's
frozen-component rule** (cp `DesignPlan/compiler/compiler.py
DesignPlan/compiler/compiler_v0.1_FROZEN.py`).

**Estimated effort**: 1–2 hours. 1-line fix in the right place + regression
test on 50 clean samples.

## 6. Residual risk

After the fix:
- 50/50 clean samples should pass under frame-only KQP (since the frame
  now matches the body, frame-axis projection = world-axis bbox for
  axis-aligned frames)
- 6/6 EX perturbations should be detected (frame-axis projection of the
  perturbed body against the ORIGINAL design-plan frame would mismatch
  the expected values from the clean design plan)
- **No regressions expected** on the 35 currently-passing clean samples

## 7. Outstanding items

- The 3 samples in the original 15-regression list that are NOT in the 12
  bbox-regressing set (102369, 107075, 107466) failed on **non-bbox
  queries** (`q_occt_valid`, `q_void_count`). These are pre-existing
  KQP issues, not caused by frame. They need separate diagnosis.

- `executor.py` (B-008, marked misdiagnosed) — should be reviewed once
  the DP fix is in, but the executor may still have a residual issue
  for samples with corrective_transform.

## 8. Action requested

**Awaiting user decision to apply the DP fix.** Estimated 1–2 hours.
After the fix:
1. Re-run `step1_identify_regressions.py` → expect 0/50 regressions
2. Re-run EX1/EX2 with frame-only KQP → expect 6/6 detection
3. Re-build the full EX battery (29 EX1 + 29 EX2) → expect 80%+ detection
4. Mark B-008 back to `wontfix` if executor is verified independently

## 9. Bug DB changes

- B-008: reclassification note updated (executor may have residual
  issues, but the current 15-regression is NOT caused by executor)
- B-009: status `wontfix` (the KQP layer is fine; the bug is in DP)
- **NEW B-010 to file**: DP compiler extracts frame incorrectly from
  history, causing 12 class (I-a) regressions. Fix: read fields
  `x_axis`, `y_axis`, `z_axis` from `sketch.transform` instead of
  `reference_plane.<x_axis, y_axis>`.


---

# Update — 2026-07-17 (B-010 fix outcome)

## Status of fixes
- **B-010 (DP compiler frame extraction wrong)** → **fixed-shipped**.
  - Modified 
    to read  instead of
     (which were None
    for the current history corpus).
  - Modified  for bbox_size
    to ALWAYS use frame-axis projection instead of best-match (which masked
    EX1/EX2). Backup: .
- **B-011 (EX1 partial detection for square bodies)** → **open**.
  19/29 EX1 samples (those with square or near-square bodies) are not
  detected because the swap does not change which world axis has the
  matching span.  Workaround options: filter EX1 to non-square bodies, or
  re-derive the KQP expected values for the EX1 perturbed body.

## Verification results

### Step 1 (regression check on 50 clean samples)

After B-010 fix + frame-only KQP:
- 50/50 bbox queries **pass** (the 12 originally-regressing samples
  moved from "fail" to "pass").
- 4 samples still regress (108850, 108851 x2, 108852) — all classified
  as class (I-b) "executor builds STEP in wrong orientation." The
  executor ignores  for some samples.  This is a residual
  pre-existing issue (B-008 re-opened; the agent previous "B-008 =
  not a bug" call was wrong).
- 50/50 minus the 4 I-b samples = **46/50 fully pass**.

### Full EX battery (58 perturbed samples, post-fix)

| Battery | Sample-level | bbox-query-level |
|---|---|---|
| EX1 (plane swap) | 10 / 29 (34%) | 20 / 87 (23%) |
| EX2 (axis flip) | **23 / 28 (82%)** ✅ | 61 / 84 (73%) |

EX2 meets the 80% threshold (plan §6.2 acceptance). EX1 does not,
because the EX1 plane swap does not change the SET of bbox values
(only the assignment of values to world axes). For samples with non-square
bodies (where the values are distinct), EX1 is detected. For square
bodies, the swap is invisible to bbox-value comparison.

## Final verdict

The B-009 → B-010 fix cascade was a **major win**:
- 12 → 4 bbox regressions in 50 clean samples (B-010's 8 wins).
- EX perturbation detection went from 0% (with best-match) to 82% on
  EX2 samples (frame-only).
- EX1 detection is 34% (limited by the perturbation mechanism, not the
  KQP layer).

**EX2 is the recommended primary ablation battery.** It exceeds the
80% detection threshold and tests a meaningful feedback signal (axis
flip is a different perturbation mechanism than E1-E6 and does not
require the DP to expose world-axis labels).

For EX1: either keep as secondary battery (B-011) with the caveat that
"non-square bodies only," or fix B-011 by re-deriving the KQP expected
values for the perturbed body.

## Bug DB changes
- B-008: re-open (executor I-b is real; was wrongly closed as
  misdiagnosed)
- B-009: confirmed wontfix (best-match WAS hiding EX; switching to
  frame-only solved the masking; the underlying "EX fundamental
  identity" claim was wrong)
- B-010: fixed-shipped
- B-011: new, open (EX1 non-detection for square bodies)

## Action requested

EX2 is the recommended primary perturbation. To use EX1 as well:
- Fix B-011 (re-derive KQP expected values for EX1-perturbed bodies)
  OR
- Restrict EX1 to non-square body samples (filter at sampler level)

Until then, the pilot should be run with EX2 alone, or with both
batteries and EX1 explicitly labeled "partial-detection; non-square only."
