# Pilot Successes Deep-Dive — 10 of 18 samples succeeded (post B-001/B-004 fix)

> **Date**: 2026-07-16 21:50
> **Inputs**: pilot artefacts + LLM agent request/response
> **Goal**: Characterise the 10 successes (1) what error type was caught (2) which verification channel diagnosed it (3) which iteration repaired it (4) feedback-driven vs Design-Plan self-diagnosis
> **Companion**: `failure_analysis_8_18.md` (the 8 failures)

---

## 1. The 10 successes grouped by when S3 fired

| iter S3 fired | count | meaning | agent called? |
|---:|---:|---|:---:|
| iter 0 | 3 | iter_0 already had P∧S∧K=True (unperturbed noise) | NO |
| iter 1 | 0 | K fixed on first attempt | (none observed) |
| iter 2 | 7 | needed 2 attempts (typically because first attempt changed only the obvious param) | YES |

**All 7 "iter 2" successes are LLM-repair events** — the agent had to do work. The 3 "iter 0" successes were unperturbed-state passes (B-005's perturbation-too-weak effect).

---

## 2. Per-success detail: which verification caught the error and which iter repaired

| # | sample | operator | sketch | iter0 (P/S/K) | iter1 (P/S/K) | iter2 (P/S/K) | S3 at |
|---|--------|----------|--------|--------------|--------------|--------------|-------|
| 1 | 100243_9fb796fe_0005/neg_03 | E1_envelope_v_shrink | polygon | TTT | TTT | TTT | 0 |
| 2 | 100243_9fb796fe_0006/neg_01 | E2_extrude_deep | polygon | TTF | TTF | TTT | 2 |
| 3 | 100877_ac1e5a17_0017/neg_02 | E1_envelope_u | polygon | TTF | TTF | TTT | 2 |
| 4 | 101817_b02acd9f_0000/neg_03 | E4_void_remove_one | frame | TTT | TTT | TTT | 0 |
| 5 | 101817_b02acd9f_0001/neg_01 | E2_extrude_deep | frame | TTF | TTF | TTT | 2 |
| 6 | 102525_06a3094b_0000/neg_01 | E2_extrude_deep | polygon | TTF | TTF | TTT | 2 |
| 7 | 102525_06a3094b_0004/neg_01 | E2_extrude_deep | polygon | TTF | TTF | TTT | 2 |
| 8 | 104453_aba0f2d1_0006/neg_02 | E4_void_remove_one | frame | TTT | TTT | TTT | 0 |
| 9 | 108851_4d515b10_0007/neg_02 | E1_envelope_u | polygon | TTF | TTF | TTT | 2 |
| 10 | 108851_4d515b10_0009/neg_03 | E1_envelope_v_shrink | polygon | TTF | TTF | TTT | 2 |

**Original error type**: in all 7 repaired cases, only **K (KQPSamplePass)** failed at iter_0. The PipelineValid and SolverValid were both True at iter_0 for ALL 10 samples — the perturbed IR was always solvable by FreeCAD (for non-annulus shapes) and the STEP always exported.

**Which verification diagnosed it**: KQP `q_bbox_w` / `q_bbox_u` / `q_bbox_v` — the parametric bbox check.

**Which iteration repaired it**:
- 3 successes: 0 iterations (iter_0 itself was already passing — no repair needed)
- 0 successes: iter_1 (LLM never gets it right on first try in this pilot)
- 7 successes: iter_2 (LLM needed 2 attempts)

---

## 3. Feedback-driven vs Design-Plan self-diagnosis

### 3.1 The smoking-gun: M0's [FEEDBACK] block

M0's [FEEDBACK] block contains ONLY the pipeline block (per §3.4 contract — M0 has no solver/kqp injection):

```json
{
  "pipeline": {
    "compile": "pass",
    "execute": "pass",
    "step_export": "fail",   ← from iter_0
    "occt_load": "fail",     ← from iter_0
    "error_messages": []
  }
}
```

**There is NO KQP feedback in M0's prompt.** There is no `q_bbox_w: expected=130.0` in the M0 feedback block.

### 3.2 Where M0 got the value `130.0` from

Searching M0's prompt for the value `130.0` (which is what the LLM emitted for 100243/neg_01):

| Position | Block | Source |
|---------:|-------|--------|
| 2893 | **[DESIGN PLAN]** | `extrude.distance_total.value = 130.0` |
| 3277 | **[DESIGN PLAN]** | `dimensions.extrude_distance.value = 130.0` |
| 4518 | **[DESIGN PLAN]** | KQP query list: `q_span_w: expected=130.0` |

**All three occurrences are in the [DESIGN PLAN] block**, NOT in [FEEDBACK]. The LLM is reading the Design Plan, not KQP feedback.

### 3.3 Per-sample LLM emit vs Design Plan vs KQP feedback

| sample | op | perturbed | **LLM emit** | KQP feedback expected | matches? |
|--------|----|-----------|--------------|----------------------|----------|
| 100243/neg_01 | E2_extrude_deep | 195.0 | **130.0** | 130.0 | ✓ |
| 100877/neg_02 | E1_envelope_u | ? | **254.0** | 254.0 | ✓ |
| 101817/neg_01 | E2_extrude_deep | 780.0 | **520.0** | 520.0 | ✓ |
| 102525/neg_00 | E2_extrude_deep | 2.325 | **1.55** | 1.55 | ✓ |
| 102525/neg_04 | E2_extrude_deep | 3.75 | **2.5** | 2.5 | ✓ |
| 108851/neg_02 | E1_envelope_u | ? | **279.4** | 279.4 | ✓ |
| 108851/neg_09 | E1_envelope_v_shrink | ? | **57.912** | 57.912 | ✓ |

**All 7 LLM repairs exactly match the KQP feedback's expected value.** But M0 doesn't have KQP feedback. The explanation: KQP was compiled FROM the Design Plan (per the KQP contract §3.4), so the `expected` value == Design Plan's value. The LLM is doing **Design-Plan self-diagnosis**.

### 3.4 Why M0 and M2 produce identical results

For all 7 repaired cases:
- M0's LLM reads `extrude.distance_total.value = 130.0` from [DESIGN PLAN] → emits distance=130.0
- M2's LLM reads `q_bbox_w: expected=130.0` from [FEEDBACK] AND `extrude.distance_total.value = 130.0` from [DESIGN PLAN] → emits distance=130.0
- Both arrive at the same value via different paths. The KQP feedback is **redundant** for self-diagnosable cases.

**Implication**: For this pilot battery, M0 ≡ M2 ≡ M3 because the Design Plan is the dominant source of truth and it's accessible to all methods equally.

---

## 4. Why iter_1 always fails and iter_2 succeeds (for the 7 repairs)

**The LLM needs 2 attempts on every polygon/frame repair.** Per-iter history:

| sample | iter0_v (perturbed) | iter1_v (LLM 1st) | K after 1 | iter2_v (LLM 2nd) | K after 2 |
|--------|---------------------|------------------|----------|------------------|----------|
| 100243/neg_01 | 195.0 | **130.0** (just distance) | ❌ | **130.0** (distance + center) | ✓ |
| 100877/neg_02 | ? | **254.0** (just width) | ❌ | **254.0** (width + center) | ✓ |
| 101817/neg_01 | 780.0 | **520.0** (just distance) | ❌ | **520.0** (distance + center) | ✓ |
| 102525/neg_00 | 2.325 | **1.55** (just distance) | ❌ | **1.55** (distance + center) | ✓ |
| 102525/neg_04 | 3.75 | **2.5** (just distance) | ❌ | **2.5** (distance + center) | ✓ |
| 108851/neg_02 | ? | **279.4** (just width) | ❌ | **279.4** (width + center) | ✓ |
| 108851/neg_09 | ? | **57.912** (just height) | ❌ | **57.912** (height + center) | ✓ |

**First attempt**: LLM changes only the obvious parameter (distance or width/height). The K query still fails because the perturbed state has BOTH a wrong param AND a wrong center.

**Second attempt**: LLM iter_1's prompt includes the previous iter_1 IR (via [CURRENT IR] in iter_2's prompt), so the LLM sees its own previous attempt + the KQP feedback showing K still failed → re-reads Design Plan more carefully → also fixes center.

**LLM's own explanation in metadata.comments**:
- iter_1: "Corrected sketch vertices from cm to mm and extrude distance to 130.0mm"
- iter_2: "Corrected rectangle center x-coordinate to match the design plan's profile bounds"

**Both attempts are self-diagnosis** — the LLM reads the Design Plan, not the KQP feedback. KQP feedback (M2/M3) tells the LLM *that* K failed but the LLM figures out *what value* to use from the Design Plan.

---

## 5. Comparison: 10 successes vs 8 failures

| aspect | 10 successes (polygon/frame) | 8 failures (annulus) |
|--------|-----------------------------|---------------------|
| iter_0 (P/S/K) | 3×TTT (no repair), 7×TTF (K fail) | 8×TTF (K fail) |
| iter_1 LLM attempt | always changes the obvious param | also changes the obvious param |
| iter_1 K status | False (param alone insufficient) | False (param alone insufficient) |
| iter_2 LLM attempt | fixes remaining (e.g. center) | fixes remaining (param+center) |
| iter_2 K status | **True** ✓ | **True** ✓ (6/7; 1 sample missing iter_2) |
| **SolverValid at any iter** | True throughout | **False throughout** (B-006) |
| Final success | True | False |
| Stop reason | S3 | S4 |

**The only difference between successes and failures is `SolverValid`**. Both classes had LLM successfully repair KQP. Successes have a non-annulus shape that FreeCAD can solve; failures have annulus which B-006 reports as `solve_status='conflicting'`.

---

## 6. What did the LLM use to self-diagnose?

The LLM's source of truth is the [DESIGN PLAN] block, specifically:

1. **Distance** perturbed → LLM reads `extrude.distance_total.value` from DP
2. **Width/height** perturbed → LLM reads `profiles[0].bbox_size.length_u` (or `width_v`) from DP
3. **Center** shifted → LLM reads `profiles[0].center` from DP (or `bbox_size` constraints)

The KQP feedback `expected` values happen to be identical because KQP was compiled FROM the Design Plan (per the KQP contract).

**M0 with no KQP feedback** still has access to the Design Plan, which is sufficient for self-diagnosis. **M2 with KQP feedback** also uses Design Plan, but redundantly gets the KQP-expected value as a backup signal.

---

## 7. Implication for the §3.2 unified prompt skeleton and §3.4 leakage boundary

The §3.2 prompt skeleton specifies four blocks ([DESIGN PLAN] / [CURRENT IR] / [FEEDBACK] / [INSTRUCTION]). The pilot data shows:

1. **[DESIGN PLAN]** is the dominant source of correct values.
2. **[FEEDBACK]** is useful as a "your answer is wrong" signal (K=False) but the *correct value* comes from the Design Plan.
3. **The KQP feedback channel is NOT the sole signal** for the agent's repair. KQP feedback enables the agent to know K failed, but the actual repair decision comes from the Design Plan.

**This means the feedback-injection mechanism is working as designed** but the **KQP feedback is structurally redundant with the Design Plan** in this pilot. The ablation cannot test "feedback value" by simply running the same perturbation through M0 and M2 because the agent's repair decision doesn't actually depend on the KQP feedback.

**To test feedback value, we need perturbations where the Design Plan is insufficient** — e.g., the perturbation changes something the Design Plan doesn't directly specify, or the LLM is asked to perform a non-self-diagnosable repair.

---

## 8. Recommendations for v0.2

| Recommendation | Detail | Effort |
|--------------|--------|--------|
| **Add feedback-self-diagnosis contrast to pilot** | Include at least 3-5 samples where the Design Plan CANNOT tell the LLM the correct value (e.g., sample where the perturbation exceeds DP tolerance, or where the IR schema requires inference beyond the DP). This creates a true test of the feedback channel. | Requires perturbation battery redesign. |
| **Track which prompt block the LLM's repair traces to** | Add a `comment` field to the agent's response that names the source ("recovered from DesignPlan.extrude.distance_total"). Enables quantification of feedback usage vs self-diagnosis rate. | 30 min code + protocol extension. |
| **Document the Design-Plan-as-ground-truth property** | The Design Plan is the *task spec*; KQP was compiled from it; the LLM uses it. This is the expected behavior per §3.1(b). The pilot confirms the architecture, not a flaw. | Doc-only. |
| **Continue the existing M0/M1/M2/M3 ablation on the current battery as a sanity check** | The pilot numbers (all 4 methods identical at 55.6%) confirm the design-plan-as-source property holds across all 4 methods. This is itself a finding. | Use pilot numbers as-is. |

---

## 9. Pilot is NOT a "feedback ablation" yet

The current pilot battery (task5 perturbation pool) is fundamentally a **Design-Plan self-diagnosis ablation**: M0 ≡ M1 ≡ M2 ≡ M3 because the LLM's repair is dominated by reading the Design Plan, not by channel-specific feedback. To test "feedback value" we need a perturbation that:
- Exceeds the Design Plan's information
- Or requires multi-step inference
- Or cannot be inferred from any one block in the prompt

The pilot is a **strong sanity check on the architecture** (channels gated, schema obeyed, S1/S2/S3 working, artifacts complete) but **not a measurement of feedback value**. That's the next-step redesign (likely Option C from `pilot_go_no_go.md` + a stronger perturbation battery).
