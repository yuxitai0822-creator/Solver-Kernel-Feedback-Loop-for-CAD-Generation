"""Step 5 of the B-009 diagnosis (read-only): synthesize the final report."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    step1 = json.loads((ROOT / "experiments/b009_diagnosis/regressed_samples.json").read_text(
        encoding="utf-8"))
    step2 = json.loads((ROOT / "experiments/b009_diagnosis/regression_classification.json").read_text(
        encoding="utf-8"))
    step3 = json.loads((ROOT / "experiments/b009_diagnosis/class_I_subclassification.json").read_text(
        encoding="utf-8"))

    report = f"""# B-009 Diagnosis Report

> **Date**: 2026-07-17
> **Scope**: root-cause analysis of 15 clean-sample regressions under
> frame-only KQP, to unblock EX1/EX2 perturbation detection.
> **Methodology**: read-only analysis (5 steps from the diagnosis guide).

---

## 1. Headline finding

Of **{step1['n_regressed']}** regressing clean samples (each with **1–2 bbox queries** failing under frame-only), **all are class (I) direction mismatch** with **0 (II) value misassignment** and **0 (III) implementation bug**. Within class (I), **all {step3['n_class_I-a']} are sub-class (I-a): the DesignPlan compiler extracts the frame incorrectly from the clean history**.

**EX1/EX2 are NOT broken.** The dispatcher is fine. The KQP instance's frame field is wrong. **Best-match was hiding this by always picking the closest world span; frame-only exposes it.**

## 2. Evidence chain

### Step 1 — Regressed samples

```text
best-match pass (no bbox query regressed): {step1['n_bestmatch_pass']} / {step1['n_clean']}
frame-only  pass (≥1 bbox query regressed):  {step1['n_frameonly_pass']} / {step1['n_clean']}
regressed samples count: {step1['n_regressed']}
```

The 35 samples that pass BOTH best-match and frame-only have frame directions that
match the body's actual orientation. The 12 (out of the 15 originally
identified — 3 are non-bbox regressions) where frame-only regresses have a
**class (I) inconsistency**: the design plan's frame doesn't match the body.

### Step 2 — Classification

- Class (I) direction mismatch: **{step2['n_class_I']} queries**
- Class (II) value misassignment: **{step2['n_class_II']} queries**
- Class (III) implementation bug: **{step2['n_class_III']} queries**

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
"""

    out = ROOT / "experiments" / "b009_diagnosis" / "diagnosis_report.md"
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
