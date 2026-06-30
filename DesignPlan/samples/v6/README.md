# Design Plan v0.6 Samples (41-50) — final sanity set batch

These 10 Design Plans use the **v0.6 schema** (`DesignPlan/DesignPlan_schema06.txt`),
addressing v0.5 weaknesses: tolerance mixed rule (relative_tol), extrude
distance single-source, multi-profile span union, part_category quantified
rules, inference_mode (none/partial/all)
(see `../../doc/DesignPlan_schema_v5评审与v6改进.md`).

**This is the LAST batch of the sanity set 50 samples.**

## Sample inventory

| # | File | Profile type | Key challenge |
|---|---|---|---|
| 41 | `107668_cf76b132_0001` | annulus | Large wheel (265mm dia) on YZ plane; relative_tol for large dims |
| 42 | `108244_329b1876_0000` | rectangle | **0 dimensions** (inference_mode=all); corrective_transform; 2.6m long |
| 43 | `108412_8de2f9c3_0000` | rectangle | Very large panel (2.4m); relative_tol critical |
| 44 | `108850_0dcd5ef1_0002` | rectangle | XZ plane with float noise on u/v |
| 45 | `108850_0dcd5ef1_0004` | rectangle | YZ plane (normal=worldX w/ noise); sibling of 44 |
| 46 | `108851_4d515b10_0005` | rectangle | YZ plane; slat family |
| 47 | `108851_4d515b10_0006` | rectangle | Sibling of 46, shorter (parametric consistency) |
| 48 | `108851_4d515b10_0007` | rectangle | XZ plane (different orient than 46/47) |
| 49 | `108851_4d515b10_0009` | rectangle | XZ plane u/v swapped vs 48 |
| 50 | `108852_fed54702_0004` | circle | Flipped frame (neg u/v); long pin (aspect 17.6) |

## Key findings

1. **inference_mode=all (42)**: 0 explicit dimensions; BOTH in-plane dims from point spans. Most under-constrained case. v0.6 inference_mode field flags this.
2. **relative_tol for large parts (41,42,43)**: 2.4m panel — v0.5 absolute-only 0.01mm would be over-strict (relative 4e-6). v0.6 relative_tol=1e-4 gives effective_tol=max(0.5, 0.244)=0.5mm.
3. **corrective_transform (42)**: u_dir label (worldZ) ≠ actual sketch-x→world-x mapping. Trust point spans.
4. **Flipped/swapped frames (48,49,50)**: u/v sign flips and swaps within same plane. Span sign-agnostic; tests frame robustness.
5. **Float noise on normals (44,45,46,50)**: ~1e-14 to 1e-16 noise on plane normal/u/v. Cleaned to unit vectors.
6. **Sibling parametric consistency (44/45, 46/47)**: same profile family, different lengths — tests compiler consistency across siblings.
