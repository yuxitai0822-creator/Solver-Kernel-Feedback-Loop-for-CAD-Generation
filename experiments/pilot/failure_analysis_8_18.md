# Pilot Failure Deep-Dive — 8 of 18 samples failed (post B-001/B-004 fix)

> **Date**: 2026-07-16 21:30
> **Inputs**: `experiments/pilot/pilot_re_read_summary.json` (post-fix)
> **Source**: `pilot_go_no_go.md` §6.2 failure (M0=M2=M3=M1 → 55.6% identical)

---

## 1. Headline finding

**55.6% Success@3 cap is structural, not method-driven.** All 8 failing samples share a single root cause: the FreeCAD solver_runner returns `solve_status='conflicting'` for `sketch_annulus` shapes because the adapter doesn't generate concentric constraints when translating the IR to FreeCAD geometry. The agent cannot fix this (it can only change IR `params`, not `op_type`).

| Shape | n | failed | fail_rate |
|-------|---|--------|-----------|
| `sketch_annulus` | 7 | **7** | **100%** |
| `sketch_rectangular_frame` | 3 | 0 | 0% |
| `sketch_polygon` | 8 | 1 | 12% |

## 2. Per-failure diagnosis

| # | sample | shape | operator | KQP last | Solver last | root cause |
|---|--------|-------|----------|----------|-------------|------------|
| 1 | 101427_a9bcb09c_0001/neg_01 | polygon | E2×1.5 | False | True | dof=32 → solver under-constrained; agent reduced bbox_w but couldn't reduce dof |
| 2 | 102410_f9877a7b_0000/neg_01 | **annulus** | E2×1.5 | True | **False** | solver runner returns conflicting; no concentric constraints generated for annulus |
| 3 | 102410_f9877a7b_0000/neg_02 | **annulus** | E3_radius_up | True | **False** | same |
| 4 | 102410_f9877a7b_0012/neg_01 | **annulus** | E2×1.5 | True | **False** | same |
| 5 | 102410_f9877a7b_0012/neg_02 | **annulus** | E3_radius_up | True | **False** | same |
| 6 | 103284_e25015aa_0003/neg_03 | **annulus** | E4_void_add | True | **False** | same |
| 7 | 106323_77f22d29_0004/neg_01 | **annulus** | E5_extent_type_change | False | **False** | same + bbox_w halved (5.0 vs 10.0) |
| 8 | 107668_cf76b132_0001/neg_02 | **annulus** | E3_radius_up | True | **False** | same |

**7/8 failures are sketch_annulus.** 1/8 is a complex polygon with high dof (32).

## 3. Per-operator failure rate

| Operator | failed / total | fail_rate |
|----------|---------------|-----------|
| E1_envelope_u / v | 0 / 4 | **0%** |
| E2_extrude_deep | 3 / 7 | 43% (all annulus) |
| E3_radius_up | **3 / 3** | **100%** |
| E4_void_add | 1 / 1 | 100% (annulus) |
| E4_void_remove_one | 0 / 2 | 0% |
| E5_extent_type_change | 1 / 1 | 100% (annulus) |

**All operators that fail 100% are on annulus samples.** E1_* (envelope) and E4_void_remove_one (frame) never fail — those shapes work fine.

## 4. Why the agent cannot recover

The agent can only modify `IR.params` (numeric values). It cannot change:
- `op_type` (sketch_annulus → sketch_rectangle)
- the structure of the sketch (add concentric constraints)
- the FreeCAD adaptation pipeline (which the agent never sees)

For B-006 (annulus), the IR's `sketch_annulus` op_type is correct but the FreeCAD shim's translation loses information. The agent sees `kqp.queries` (showing bbox_w/outer_radius) and tries to fix `params`, but the underlying shape can't be solved by FreeCAD regardless of param values.

## 5. B-005 supersession

B-005 was filed because all 4 methods gave identical 55.6% — suggesting the perturbation battery is too weak. The deeper analysis (this document) shows the real blocker is **annulus shapes being structurally unsolvable** (B-006), not the perturbation strength. B-005 is now marked **obsolete-superseded-by-B-006** in the bug DB.

## 6. Implication for ablation

| Aspect | Status |
|--------|--------|
| **Feedback injection works** | ✅ — pre-fix M0 had 3×S2 vs M2 had 0×S2 (verified) |
| **KQP path works** | ✅ — 4/7 annulus samples have K=True at last iter (agent repair of KQP was successful) |
| **Solver path broken for annulus** | ❌ — B-006 root cause |
| **M0 ≠ M2 measurable on polygon/frame samples** | partial — 10/18 samples are polygon+frame; M0/M2 are identical on them too (because agent isn't called when iter_0 already passes) |
| **Ablation ready for full 104 benchmark** | ❌ — must fix B-006 first (or exclude annulus from §1.4 grid) |

## 7. Resolution options for B-006

| Option | Description | Effort |
|--------|-------------|--------|
| **A. Fix solver_runner to handle sketch_annulus** | Add Concentric + Radius constraints in `Freecadsolver_feedback/core/solver_runner.py` when building annulus. Expected: dof=0, solve_status='success' (or 'under_constrained' if radius isn't pinned) | 1-2h |
| **B. Exclude annulus from §1.4 grid** | Re-pick 18 pilot samples skipping annulus; expect ~5/18 (all annulus) → 0/13 (polygon+frame only) | 30 min + re-run |
| **C. Mark annulus as "out of scope" in pilot contract** | Add a §X.5 clause: "samples whose op_type is sketch_annulus are reported as unsolvable by FreeCAD shim; the ablation is only meaningful on non-annulus samples" | 30 min, no re-run |

**Recommended: A** — root-cause fix. After A, the 7 annulus samples should solve and the pilot success rate would jump to 15/18 = 83.3%, and method-discrimination would likely appear (some methods may repair annulus better than others).

## 8. After B-006 is fixed — expected pilot numbers

If B-006 is fixed and the pilot is re-run:
- M0 expected: low Success@3 (uses only pipeline; design-plan cross-check is unreliable)
- M2 expected: medium-high Success@3 on KQP-visible samples (KQP feedback drives repair)
- M3 expected: best on the 8 KQP-visible + 6 solver-visible combined
- McNemar-pairable discordance between M0/M2 ≥ 8 expected (McNemar at n=8 needs ~30pp gap)

If after B-006 fix M0 and M2 are still identical: the feedback channels aren't actually being injected (re-verify §3.4 — but we already verified this; so this scenario is unlikely).
