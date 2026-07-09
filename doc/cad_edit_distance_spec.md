# CAD Editing Distance v0.1 — Specification

> **Version**: 0.1
> **Date**: 2026-07-09
> **Status**: FROZEN

---

## 1. Purpose

Quantify how much a CAD IR was modified between two consecutive repair-loop
iterations (IR_t → IR_{t+1}).  Three metrics with different semantics.

```
CAD Editing Distance:
    CED_text        (raw IR string similarity)
    CED_declared    (declared operation sequence similarity)
    CED_executed    (runtime trace similarity)
```

CED_declared is the **primary** metric; CED_text is the fallback when IR
cannot be parsed or normalized; CED_executed is a runtime-analysis auxiliary.

---

## 2. Definitions

### 2.1 CED_text

Levenshtein over the raw IR JSON text, normalized:

```
CED_text = Levenshtein(raw_IR_t, raw_IR_{t+1})
         / max(1, max(len(raw_IR_t), len(raw_IR_{t+1})))
```

* Returns a dict: `{raw, normalized, text_a_len, text_b_len}`
* `normalized ∈ [0, 1]`, clipped if raw value > 1
* Used as fallback when declared/executed metrics are unavailable

### 2.2 CED_declared

Weighted edit distance between the two IRs' normalized declared operation
sequences.

```
CED_declared = Σ match_cost(m) / max(1, TotalOpWeight)
```

Where:

* `TotalOpWeight(IR) = Σ base_weight(op)` for all ops in IR
* `match_cost(m)` is computed per matched-op entry (see §4)

| Metric | Value |
|---|---|
| `n_ops_a` / `n_ops_b` | declared op counts in IR_t / IR_{t+1} |
| `weight_a` / `weight_b` | total op weight |
| `raw` | sum of match_cost (unclipped) |
| `normalized` | raw / max(weight_a, weight_b, 1), clipped to [0, 1] |
| `breakdown.n_matches_added/deleted/matched` | counts |
| `breakdown.by_kind` | per-op_type cost breakdown |
| `breakdown.match_pairs` | per-match detail |

### 2.3 CED_executed

Same as CED_declared, but applied to the runtime traces
(declared_operation_trace.json → executed_operation_trace.json).

Per-op runtime status: `success` | `failed` | `skipped`.  Match cost
doubles for `failed` ops (penalty for execution-time failures).

### 2.4 RepairCost (v0.1 simplified)

```
RepairCost = Σ CED_declared_raw(IR_t, IR_{t+1})  [for t = 1..N-1]
           + 0.1 × #execution_attempts
           + 0.1 × #verification_calls
```

`#verification_calls = #solver_calls + #kqp_calls`.

---

## 3. Operation matching strategy

Operations are matched between seq_a (IR_t) and seq_b (IR_{t+1}) in this order:

1. **Exact op_id match** — preferred.
2. **Role match** — same `role` (e.g., `base_profile`, `base_body`).
3. **op_type match** — same `op_type`.
4. **Remaining unmatched** → all marked `added` (in seq_b) or `deleted` (in seq_a).

Returns a list of `match` dicts:
```json
{"a_op": <op or null>, "b_op": <op or null>,
 "match_kind": "matched"|"added"|"deleted",
 "match_by": "op_id"|"role:..."| "op_type:..." | "unmatched_..."}
```

---

## 4. Match-cost table

For each matched op pair, the cost is:

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
| add / delete boolean op (cut/join) | 4 |
| add / delete topology op (export_step) | 1 |
| profile type change (rect→circle etc.) | 4 |
| boolean operation change (cut↔join) | 4 |
| topology structure change (any other type switch) | 5 |
| full rewrite flag | 8 |
| `path` field (export_step) | **EXCLUDED** (not semantically part of CAD) |

For a single matched op, all applicable deltas are summed.

For unmatched ops:
* `added` op in seq_b: cost = `add_delete_cost(op_type)`
* `deleted` op in seq_a: cost = `add_delete_cost(op_type)`

---

## 5. Base weights (per op_type)

| op_type | base_weight |
|---|---|
| `sketch_rectangle` | 2 |
| `sketch_circle` | 2 |
| `sketch_annulus` | 2 |
| `sketch_rectangular_frame` | 2 |
| `sketch_stadium` | 2 |
| `sketch_polygon` | 2 |
| `extrude` | 3 |
| `cut` | 4 |
| `join` | 4 |
| `add_constraint` | 2 |
| `set_dimension` | 2 |
| `export_step` | 1 |

A rectangle-only IR has total weight 2 + 3 + 1 = 6.

---

## 6. Metric selection rule

| IR state | Primary | Auxiliary |
|---|---|---|
| Either IR JSON parse failed | `CED_text` | none |
| Either IR schema invalid | `CED_text` | partial CED |
| Both IR parse + normalize ok | **`CED_declared`** | `CED_text` |
| Both have runtime trace | `CED_declared` | `CED_executed`, `CED_text` |
| Adaptor/runtime failed but IR ok | `CED_declared` | `CED_text`, `CED_executed` |
| Both executed successfully | `CED_declared` | `CED_executed`, `CED_text` |

The implementation in `compute_ced.compute_all()` returns:
```json
{"primary_metric": "CED_declared", "primary_value": 0.21,
 "primary_raw": 1.5, "ced_text": {...}, "ced_declared": {...}, "ced_executed": {...}}
```

---

## 7. Implementation

```
cad_edit_distance/
  normalize_ir.py       # IR → normalized op list
  op_matcher.py         # match ops by op_id / role / op_type
  edit_cost.py          # cost table + per-match computation
  compute_ced.py        # CED_text, CED_declared, CED_executed, RepairCost
  generate_edit_cases.py  # 48 manual edit cases
  tests/manual_edit_cases/case_NN.json
  reports/ced_validation_report.json
```

---

## 8. Validation outcomes (48 manual edit cases)

| Category | Count | CED_declared range |
|---|---|---|
| no_change | 1 | 0.0000 (raw 0) |
| param_edit | 37 | 0.1667 – 0.5000 (raw 1–3) |
| add_op | 5 | 0.5000 – 0.7500 (raw 3–5) |
| change_type | 3 | 0.5000 – 0.7500 (raw 3–5) |
| delete_op | 1 | 0.1667 (raw 1) |
| topology_change | 1 | 1.0000 (raw 8) |

| Metric | Count | Rate |
|---|---|---|
| CED_declared available | 48 / 48 | 100% |
| CED_text fallback | 0 / 48 | 0% |
| CED_executed available | (when trace present) | n/a |

All 48 cases produced sensible ranking: `no_change < param_edit < add/delete < change_type < topology_change`.

---

## 9. Repro

```bash
python cad_edit_distance/generate_edit_cases.py
# regenerates cad_edit_distance/tests/manual_edit_cases/case_NN.json
# and reports/ced_validation_report.json

# Single-pair computation:
python -c "
import sys, json
sys.path.insert(0, 'cad_edit_distance')
from compute_ced import compute_all
a = json.load(open('cad_ir/samples/manual_ir_examples/100243_9fb796fe_0005.cad_ir.json'))
b = json.load(open('cad_ir/samples/manual_ir_examples/100243_9fb796fe_0006.cad_ir.json'))
print(json.dumps(compute_all(a, b), indent=2))
"
```

---

## 10. Limitations (v0.1)

1. **op_matcher is greedy + heuristic, not optimal Hungarian.**  Some matchings
   may be sub-optimal; V0.2 should use scipy.optimize.linear_sum_assignment
   to find the minimum-cost matching.

2. **No semantic equivalence for profile types.**  rectangle → rectangle with
   swapped width/height registers as a 2-param edit (cost 2), not as a
   semantic-preserving edit (cost 0).  V0.2 should add shape-normalization
   rules.

3. **No repair-loop state tracking.**  RepairCost tracks only CED_declared
   and simple counts.  V0.2 should add token cost, latency, and feedback
   type tracking.

4. **CED_executed is symmetric for success/failed status.**  We treat
   `failed` ops as `added`/`deleted` for matching.  V0.2 should differentiate
   them with explicit failure-cost penalties.

5. **Full rewrite flag (cost 8) is NOT auto-detected.**  V0.1 reports raw
   cost; V0.2 should add a "rewrite threshold" detector (e.g., CED > 0.8
   → flag rewrite, cost 8).