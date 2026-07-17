# Ablation Study Pre-validation Report

> **Date**: 2026-07-15
> **Stage**: Pre-M0/M1/M2/M3 run, after History2IR V0.1.4 freeze
> **Population**: 46 clean samples + 104 repair-eligible negatives
> **Statistical plan**: paired McNemar at the sample level (Success@3)
> **Companion artifacts**: `repair_eligible_manifest.json`, `compile_summary.json`

This report audits the **two statistical risks** of the planned ablation study before
any LLM calls are made, per the workflow rule "前验分析 ≥ 主实验" (pre-validation is
at least as important as the main experiment).

---

## 1. Per-intent coverage audit (the "per-intent evidence-chain" risk)

**Question**: are all 5 design intents covered with enough eligible negatives to
support per-intent analysis, or are some intents sparse / empty?

### 1.1 Population matrix (104 / 132 eligible = 78.8%)

| `target_intent`        | Eligible | Total | Ratio | Per-operator breakdown (eligible) |
|------------------------|---------:|------:|------:|------------------------------------|
| `bbox_size`            | **88**   | 92    | 95.7% | E2_extrude_deep 43, E1_envelope_u 22, E1_envelope_v_shrink 22, E2_extrude_shallow 1 |
| `through_void_count`   | **10**   | 20    | 50.0% | E4_void_add 8, E4_void_remove_one 2 |
| `cylinder_radius`      | **5**    | 19    | 26.3% | E3_radius_up 5 |
| `symmetric_about_plane`| **1**    | 1     | 100%  | E5_extent_type_change 1 |
| `is_solid`             | **0**    | 6     | **0.0%** | (all 6 blocked at repair-eligibility) |
| **Total**              | **104**  | 138   | 75.4% |                                      |

> The "eligible" numerator is the intersection of (a) clean compile passes the IR
> validator and (b) the perturbed IR can be loaded + step-exported + step-KQP'd
> with `sample_agree=True` and `targeted_failure_preserved=True`.

### 1.2 Intent-level holes

| Intent                | Status    | Why | Mitigation |
|-----------------------|-----------|-----|------------|
| `is_solid`            | **HARD HOLE** | All 6 source negatives are `E6_inner_gt_outer` (set inner_radius > outer_radius in annulus). The perturbed geometry is **invalid**, so neither the history-STEP nor the IR-STEP can be loaded — both fail at adaptor export. The negatives are therefore never repair-eligible. | Drop `is_solid` from per-intent analysis. Annotate in §6 of paper as "design intent not surfaced in our perturbation battery because no perturbation in our taxonomy can produce a valid-shape but solid-flag-violating case". |
| `symmetric_about_plane` | **MARGINAL** | Only 1 sample (106323_77f22d29_0004) has this intent. The perturbation (`E5_extent_type_change`) actually flips bbox_w, not `q_symmetric`. | Report as a single-case qualitative observation only; do **not** claim significance. |
| `cylinder_radius`     | **SPARSE** | 5 / 19 eligible. The 14 not-eligible are blocked by the IR's polygon-flattening of arcs (a V0.2 limitation; see task2_freeze_report §5). | n=5 is at the borderline of "descriptive only". Do not run statistical test on this intent alone; aggregate with `bbox_size` if needed. |
| `through_void_count`  | **OK**     | 10 negatives, mix of E4_void_add / E4_void_remove_one. Both operator types show up. | McNemar is feasible per-operator-pair but not per intent with such small n; treat as descriptive. |
| `bbox_size`           | **ROBUST** | 88 negatives, 4 operator types, all three query directions. | This is the statistical backbone of the study. |

### 1.3 Decision: per-intent analysis scope

- ✅ **Quantitative main table** — overall `bbox_size` only (88 paired samples).
- ✅ **Quantitative per-operator breakdown** — `E1_envelope_u/v`, `E2_extrude_deep/shallow`,
       `E4_void_add`, `E4_void_remove_one`, `E3_radius_up` (one table, one McNemar per row).
- ❌ **No statistical claims** about `is_solid`, `symmetric_about_plane`, or the
       `cylinder_radius`-only subgroup.  These go into the **descriptive** part of
       the per-intent table and must be explicitly labelled "n<10, descriptive only".

---

## 2. Per-perturbation feedback-channel visibility matrix (the "explain-the-delta" risk)

**Question**: for each perturbation type, which feedback channel can see the
perturbation?  This determines the upper bound on what M0→M1 / M0→M2 / M0→M3
can possibly show.

### 2.1 Channel visibility

Definitions:
- **Solver visible** = the perturbation produces an observable change in
  the solver's diagnosis (DoF, conflict, redundancy, recompute failure, or
  invalid-geometry marker) for the rebuilt FreeCAD Sketcher representation.
- **KQP visible** = the perturbation produces at least one `status=fail`
  query in the history-built STEP's KQP result.

| Operator                  | Solver? | KQP?  | Reasoning                                                                                                                                                       | Eligible |
|---------------------------|:-------:|:-----:|------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------:|
| `E1_envelope_u`           | ✗       | ✓     | Single sketch dimension change. Solver sees fully-constrained sketch (unchanged DOF). KQP `q_bbox_u` fires.                                                     | 22       |
| `E1_envelope_v_shrink`    | ✗       | ✓     | Same as above with v-axis.                                                                                                                                       | 22       |
| `E2_extrude_deep`         | ✗       | ✓     | Extrude depth change, sketch unchanged. Solver unaffected. KQP `q_bbox_w` fires.                                                                                 | 43       |
| `E2_extrude_shallow`      | ✗       | ✓     | Same as above.                                                                                                                                                   | 1        |
| `E3_radius_up`            | △       | ✓     | Solver MAY see DOF change if arc→line degeneration, but not always. KQP `q_outer_radius` fires. **Polygonal IR loses radius info → only 5/19 eligible.**            | 5        |
| `E4_void_add`             | ✓       | ✓     | Adds an inner loop → solver under-constrained check fires AND KQP `q_radius` fires (was disk → annulus flips radius from "single" to "inner+outer").              | 8        |
| `E4_void_remove_one`      | ✓       | ✓     | Removes an inner loop → solver over-constrained check fires AND KQP `q_void_count` fires.                                                                        | 2        |
| `E5_extent_type_change`   | ✗       | ✓     | Only extrude.extent_type changes (symmetric ↔ one_side ↔ two_sides). Sketch unchanged → solver blind. KQP `q_bbox_w` fires when symmetry flips bbox.                | 1        |
| `E6_inner_gt_outer`       | ✓       | ✓     | Annulus with inner > outer → solver reports invalid constraint AND KQP `q_occt_valid` fails. **But adaptor refuses to export → 0 eligible.**                      | 0        |

Legend: ✓ = visible; ✗ = invisible; △ = conditionally visible.

### 2.2 Method × leverage split

The "leverage" of each method is determined by which channels the perturbations
it processes go through:

| Method        | Feedback channels          | Eligible negatives reachable |   n   |
|---------------|----------------------------|-------------------------------|------:|
| M0 (baseline) | (none)                     | all                           | 104   |
| M1 (solver)   | Solver only                | E3 (5, partial) + E4 (10)     | **15** |
| M2 (KQP)      | KQP only                   | E1 (44) + E2 (44) + E5 (1)    | **89** |
| M3 (both)     | Solver + KQP (union)       | all except E6 (0)             | **104** |

> Implication for the analysis:
> **M1 vs M0** can only differ on the **15 negatives** in the "solver-visible"
> subset. If M1 ≠ M0 globally, the improvement MUST come from those 15 negatives.
>
> **M2 vs M0** can only differ on the **89 negatives** in the "KQP-visible"
> subset. Improvement here is the "easy win" because the perturbations are
> bbox/depth/extrude-type only — KQP always catches them.
>
> **M3 vs M2** can only differ on the **15 negatives** where solver has additional
> leverage over KQP. This is where the "double feedback" claim must earn its keep.
>
> **M3 vs M1** can only differ on the **89 negatives** where KQP has additional
> leverage over solver. Same story, mirror direction.

### 2.3 Method leverage table (recommended format for the paper)

| Method | Reachable subset | McNemar n | Expected direction |
|--------|------------------|----------:|--------------------|
| M1 vs M0 | solver-visible  | 15 | If M1>M0, it shows here. n=15 has power for ~40pp gap. |
| M2 vs M0 | kqp-visible     | 89 | M2 should be substantially better; 89 is overkill. |
| M3 vs M2 | solver-visible  | 15 | M3's value vs M2 = solver's added value on this 15. |
| M3 vs M1 | kqp-visible     | 89 | M3's value vs M1 = KQP's added value on this 89. |

### 2.4 "Why M1 might look weak" — the explanation arm

M1 should be reported with a **per-operator split**, not just an overall M1 vs M0
p-value. If M1 ≈ M0 overall but M1 > M0 on the `E4_void_*` rows, that is the
honest finding:

> "M1's solver feedback has measurable leverage on E4 (void add/remove) where
> sketch DoF and redundancy are the right signals, but no leverage on E1/E2/E5
> where the perturbation is invisible to the solver. The weak overall M1 signal
> is therefore expected from the visibility table, not a failure of the solver."

This framing is the **kill-the-paper-with-honesty** defense: the visibility table
predicts what each method can / cannot win, so any per-method result that
contradicts it (e.g. M1 > M2 overall) becomes a paper-worthy surprise, and any
result that confirms it (e.g. M2 >> M1 because M1's subset is small) is **not
a failure but a finding**.

---

## 3. McNemar power analysis (the "main-table significance" risk)

### 3.1 Setup

- 104 paired samples, one Success@3 binary outcome per (sample, method).
- McNemar's test on discordant pairs (cases where M_a succeeds and M_b fails, vs
  the reverse).  Test statistic = (|b-c|-1)²/(b+c).
- α = 0.05, target power = 0.8.

### 3.2 Power at n = 104 (overall)

| Success-rate gap (M_b − M_a) | Expected discordant (104 × p_b + 104 × p_a − 2×p_a×p_b)| Detectable? |
|------------------------------|---------------------------------------------------------:|:-----------:|
| 5 pp  (e.g. 0.30 vs 0.35)    | ~7                                                       | ✗           |
| 10 pp (0.30 vs 0.40)         | ~14                                                      | △ borderline |
| 15 pp (0.30 vs 0.45)         | ~21                                                      | ✓           |
| 20 pp (0.30 vs 0.50)         | ~28                                                      | ✓✓          |

→ If the **M3 vs M0 advantage is 15pp or larger**, the main table is statistically
powered at n=104.  If it's only 5pp, the main table will not reject H0 and we
must report null-result with confidence-interval framing rather than significance.

### 3.3 Power at n = 15 (M1's leverage subset)

| Success-rate gap | Detectable? (n=15) |
|------------------|:------------------:|
| 30 pp            | ✓ (borderline)     |
| 40 pp            | ✓                  |
| < 30 pp          | ✗                  |

→ M1's wins on the solver-visible subset, if they exist, need to be **large**
(40pp+) to clear McNemar at n=15.  If they are smaller, report as
"observed improvement, descriptive only" and use a binomial confidence interval.

---

## 4. Pre-validation summary

| Question | Answer |
|----------|--------|
| Is 104 enough for the main M0–M3 paired comparison? | **YES** for ≥15pp effects. |
| Is per-intent analysis safe across all 5 intents? | **NO.** `is_solid` is a hard hole (n=0); `symmetric_about_plane` is marginal (n=1); `cylinder_radius` is sparse (n=5). Only `bbox_size` (n=88) and (per-operator) `E4_void_*` (n=10) are quantitatively usable. |
| Is the per-perturbation visibility table actionable? | **YES.** Method comparison should be reported **per-operator**, not just overall. This explains M1's narrow leverage and pre-empts reviewer concerns about "weak" M1 signal. |
| Are there risks of the main table being under-powered? | **YES** if M3-M0 < 15pp. We must pre-register a "descriptive-only" fallback in the paper methods. |
| Should we drop `E6_inner_gt_outer` from analysis? | **YES** — it is fully outside the eligible set (0 negatives). It is mentioned only for completeness. |
| Should we expand the perturbation battery to cover `is_solid`? | **V0.2 work.** New operators could include flipping a `hole()` to a `boss()` or a `boolean_op` parameter swap. Not in scope of current study. |

---

## 5. Pre-registered analysis plan

1. **Main table**: 104 paired samples × 4 methods. Per-sample Success@3 binary.
   McNemar pairwise (M3 vs M2, M3 vs M1, M2 vs M1, M3 vs M0).  Report
   exact p-values from `statsmodels.stats.contingency.mcnemar` and 95% Wilson
   CIs on Success@3 rates.
2. **Per-operator table**: 8 rows (one per perturbation operator). Each row is
   McNemar on that operator's eligible subset.  Mark `<10` rows as
   "descriptive only".
3. **Per-intent table**: 5 rows (one per target_intent). Mark `is_solid`,
   `symmetric_about_plane`, and `cylinder_radius` rows as descriptive-only.
4. **Visibility-marginal analysis**: for each (method, perturbation) pair, report
   whether the visibility table predicts an improvement. Use this to **interpret**
   null results, not to filter them.
5. **Token / cost table**: secondary, count mean/median tokens per iteration per
   method.  Documented as informational only.

---

## 6. Concrete instructions for the next run

1. The 104 eligible negatives are listed in
   `experiments/history2ir/reports/repair_eligible_manifest.json`.  Use that
   manifest as the run set — **do not** include any of the 34 non-eligible
   negatives; they cannot contribute to repair.
2. For each (sample, negative, method), call the existing
   `cad_repair_loop.repair_loop.run_repair_loop` with the
   method's feedback disabled (set the appropriate config flag).
3. Use temperature 0.0 and max iterations 3 (frozen components, see
   `doc/frozen_components_for_repair_benchmark.md`).
4. Save per-iteration results to
   `experiments/results/<METHOD>/<sample_id>/<negative_id>/iteration_<N>.json`
   following `experiment_contract_v0.1.md`.

---

## 7. Honest scope statement (paper draft)

> "Our ablation compares four methods (M0/M1/M2/M3) on 46 samples and 104
> repair-eligible negatives. The eligible set is governed by the History2IR
> compiler's representational fidelity; specifically, the `is_solid` design
> intent is not exercised (0 eligible negatives) and `cylinder_radius` is
> sparsely represented (5/19 eligible) due to the parser's polygon
> approximation of arcs. Per-intent statistical claims are therefore only
> supported for `bbox_size`; other intents appear as descriptive observation.
> The per-perturbation visibility analysis (§2) predicts that M1's leverage is
> confined to ~15 negatives (solver-visible subset) and M2's leverage to ~89
> negatives (KQP-visible subset); we therefore report per-operator breakdowns
> alongside the overall ablation and interpret results in light of this
> visibility asymmetry."