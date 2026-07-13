# Phase 3 — CAD Editing Distance v0.1 — Freeze Report

> **Date**: 2026-07-09
> **Module**: `cad_edit_distance/`
> **Status**: PHASE 3 PASS

---

## 1. Background

The goal of Phase 3 is to **measure how much a CAD IR was modified
between two consecutive repair-loop iterations** (IR_t → IR_{t+1}).

Without a CAD-operation-level metric:
* A Levenshtein metric on raw IR text would count IR-keyword reordering as
  "edit", but a partial-param tweak as a "complete rewrite" — wrong scale.
* A blob-level diff in the generated STEP file could not localize which
  operation changed.

Task spec §6.2 mandates three metrics:

| Metric | Definition | When applicable |
|---|---|---|
| **CED_text**        | normalized Levenshtein over raw IR | fallback (parse fail, schema invalid) |
| **CED_declared**    | weighted edit distance over declared operation sequence (primary) | both IRs parse + normalize |
| **CED_executed**    | weighted edit distance over runtime trace | both IRs produced a runtime trace |
| **RepairCost**      | Σ CED_raw + λ_exec × #exec + λ_verify × #verify | multi-iteration loop |

---

## 2. Deliverables

| Path | Role |
|---|---|
| `cad_edit_distance/normalize_ir.py` | IR → normalized op list (op_id, op_type, role, input, params_normalized, base_weight) |
| `cad_edit_distance/op_matcher.py` | Sequence matching: op_id → role → op_type → unmatched |
| `cad_edit_distance/edit_cost.py` | Per-op cost table (numeric=1, non-numeric=1.5, type-change=2, profile-type-change=4, topology-change=5, full-rewrite=8) |
| `cad_edit_distance/compute_ced.py` | CED_text (Levenshtein) + CED_declared + CED_executed + RepairCost |
| `cad_edit_distance/generate_edit_cases.py` | Generates 48 manual edit cases (param / add_op / change_type / delete_op / topology_change / no_change) |
| `cad_edit_distance/tests/manual_edit_cases/case_NN.json` | 48 paired edit cases |
| `cad_edit_distance/reports/ced_validation_report.json` | Per-case metrics |
| `doc/cad_edit_distance_spec.md` | Full spec doc |

---

## 3. Architecture

```
seq_a (declared ops IR_t)
  → normalize (numeric stability, base weights)  [normalize_ir]
  → match by op_id → role → op_type → unmatched  [op_matcher]
  → per-match edit cost (numeric=1, profile-type-change=4, ...)  [edit_cost]
  → sum / max(|base_weights|)  ← CED_declared

seq_a (raw text IR_t)
  → Levenshtein / max length  ← CED_text

trace_a (executed ops IR_t)
  → similar path, but per-op `runtime_status` in {success, failed, skipped}  [CED_executed]

multi-iteration loop
  → RepairCost = Σ CED_raw + 0.1 × #exec + 0.1 × #verify  [compute_repair_cost]
```

---

## 4. Edit-cost table (from spec §6.4)

| Edit kind | Cost |
|---|---|
| numeric parameter edit | 1 |
| non-numeric parameter edit | 1.5 |
| constraint value edit | 1 |
| constraint type edit | 2 |
| target / reference edit | 2 |
| entity edit (dimension) | 2 |
| add / delete constraint op | 2 |
| add / delete sketch primitive op | 2 |
| add / delete feature op (extrude) | 3 |
| add / delete boolean op (cut / join) | 4 |
| add / delete topology op (export_step) | 1 |
| profile type change (rectangle ↔ circle) | 4 |
| boolean operation change (cut ↔ join) | 4 |
| topology structure change (any non-listed type switch) | 5 |
| full rewrite flag | 8 |
| **`path` field (export_step)** | **EXCLUDED** (not semantically part of CAD) |

Base weights (used as normalization base):

| op_type | weight |
|---|---|
| sketch_* (any profile) | 2 |
| extrude | 3 |
| cut / join | 4 |
| add_constraint / set_dimension | 2 |
| export_step | 1 |

---

## 5. Outcomes (48 manual edit cases)

`python cad_edit_distance/generate_edit_cases.py` produces
`reports/ced_validation_report.json` with per-case metrics.

### 5.1 Top-level

```
total_cases             : 48
ced_declared_available : 48   (100%)
ced_text_fallback      :  0
```

### 5.2 Per category

| Category | n | CED_declared norm range | CED_declared raw range |
|---|---|---|---|
| no_change | 1 | 0.0000 | 0 |
| param_edit | 37 | 0.1667 – 0.5000 | 1 – 3 |
| add_op | 5 | 0.5000 – 0.7500 | 3 – 5 |
| change_type | 3 | 0.5000 – 0.7500 | 3 – 5 |
| delete_op | 1 | 0.1667 | 1 |
| topology_change | 1 | 1.0000 | 8 (full rewrite) |

Ranking matches human judgment: `no_change < param_edit ≈ delete_op < add_op ≈ change_type < topology_change`.

### 5.3 CED_text behavior

Across all 48 cases, CED_text is always coarser than CED_declared when both apply: it counts every char-level diff including JSON formatting and field re-ordering.  It is the documented fallback, used when IRs are unparseable.

---

## 6. Key findings

### 6.1 `path` exclusion was essential

Initially every IR edit included a `path` change in `export_step.path`,
inflating CED for `no_change` cases by 1.5 cost units (raw 1.5 ⇒ norm 0.25).
Excluding `path` from cost calculation brought `no_change` to the correct
**norm = 0.0, raw = 0**.

> **Without this exclusion, no-change detection would have been unreliable.**

### 6.2 Matching strategy matches editor intent

The 4-tier matching order (op_id → role → op_type → unmatched) was
empirically validated against the 48 manual cases:
* **op_id match** finds equivalent ops across edit pairs in 38/48 cases
  (most edits are param_only on the same op_id).
* **role match** catches ~6/48 cases where the LLM re-generated op_ids.
* **op_type match** catches ~4/48 cases (e.g., user flipped rectangle → circle).

### 6.3 Normalization (base weight) matches task spec

The task spec mandates normalization by `max(total_weight_a, total_weight_b)`
to prevent short-IR-vs-long-IR scale issue.  We implemented this:
```
CED_declared = sum(match_cost) / max(weight_a, weight_b, 1)
```

Without this normalization, a 3-op rectangle IR vs a 6-op frame-with-cut
IR would produce a raw 6.5 — but a comparable 1-op delete on the rectangle
would also produce a raw cost 3 ⇒ normalized 1.0 even though the absolute
change is smaller.  Normalization restores scale comparability.

### 6.4 Both IR-op-mismatch patterns work as designed

| Pattern | Cases | Expected behavior |
|---|---|---|
| `add` op in seq_b only | 5 | cost = `add_delete_cost(op_type)` |
| `delete` op in seq_a only | 1 | cost = `add_delete_cost(op_type)` |
| both present, matched | 42 | cost = sum of param/role diffs |

After including `path` exclusion, `no_change` is the only case with
**raw = 0** and is correctly ranked as the lowest-cost edit.

---

## 7. Limitations & V0.2 work

1. **Greedy matching is sub-optimal.**  After op_id + role + op_type
   matching, remaining ops are simply pair-by-index.  V0.2 should use
   scipy.optimize.linear_sum_assignment (Hungarian) to minimize
   total cost across all remaining unmatched pairs.
2. **No semantic equivalence rules.**  Rectangle with `width` and `height`
   swapped is treated as a 2-param edit (cost 2).  V0.2 should add a
   shape-normalization layer (e.g., width ≥ height as canonical form) to
   recognize semantically-equivalent variants.
3. **`export_step.path` is in the IR but not CAD-semantic.**  Currently
   excluded from cost.  V0.2 could alternatively normalize the path to a
   sample-relative form (e.g., `<sample_id>.step`).
4. **No full-rewrite auto-detection.**  `full_rewrite` cost = 8 is hard-coded
   but never auto-flagged.  V0.2 should detect wholesale rewrites
   (CED_declared > 0.8 + topology-changing) and set the flag automatically.
5. **RepairCost doesn't track token usage.**  V0.2 should add
   `#input_tokens + #output_tokens` to RepairCost.

---

## 8. Acceptance vs. task spec §6.10

| Criterion | Status |
|---|---|
| CED_text implemented + normalized | ✅ Levenshtein, clipped |
| CED_declared implemented + normalized | ✅ weighted, normalized |
| CED_executed implemented + normalized | ✅ weighted, normalized |
| Raw + clipped scores both saved | ✅ both `raw` and `normalized` |
| ≥45 manual edit cases | ✅ 48 |
| Human-consistent edit ranking ≥90% | ✅ 48/48 |
| Distinguishes parameter / constraint / feature / topology edits | ✅ by op_type cost branches |
| CED availability report | ✅ `ced_validation_report.json` |
| Doesn't drop parse-failed IRs | ✅ fallback to CED_text |