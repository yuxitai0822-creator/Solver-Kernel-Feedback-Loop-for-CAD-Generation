# Design Plan v0.5 Samples (31-40)

These 10 Design Plans use the **v0.5 schema** (`DesignPlan/DesignPlan_schema05.txt`),
which addresses v0.4 weaknesses found when samples 31-40 introduced symmetric
extrusion, degenerate two_side, dimension-less arbitrary_closed profiles, and
positive-distance-but-negative-direction anomalies
(see `../../doc/DesignPlan_schema_v4评审与v5改进.md`).

## Sample inventory

| # | File | Profile type | Key challenge |
|---|---|---|---|
| 31 | `105278_909f3813_0000` | rectangle | Construction diagonals; offset plane origin |
| 32 | `106323_77f22d29_0004` | annulus | **Symmetric extrude** (z straddles ±2.5mm); offset plane origin |
| 33 | `106817_bb28b7aa_0002` | circle | Offset center (114.3mm); 0 constraints |
| 34 | `106817_bb28b7aa_0003` | circle | Offset center (50.8,-63.5); 0 constraints |
| 35 | `106817_bb28b7aa_0004` | annulus | Offset center (-25.4,12.7); explicit concentric |
| 36 | `107055_0500fdd1_0027` | annulus | **Positive distance but -Z body** (direction anomaly); implicit concentric via 2 Coincident; deep plane offset |
| 37 | `107075_beb19139_0000` | **arbitrary_closed** | 2 arc + 2 line non-stadium; NO dimensions; YZ plane |
| 38 | `107466_72cd4ce9_0002` | stadium+2holes | **Degenerate two_side** (extent_two=0); EqualConstraint |
| 39 | `107467_a8afc51d_0000` | circle | Simple pivot (baseline) |
| 40 | `107467_a8afc51d_0002` | circle | Sibling of 39, longer extrude |

## Key findings encoded in these samples

1. **Symmetric extrude (32)**: `extent_type=symmetric`, `direction=both_symmetric`, distance_total=2×half-extent. v0.4 `both` lost symmetric semantics.
2. **Degenerate two_side (38)**: `extent_type=degenerate_two_side`, extent_two=0 → effectively one_side. v0.4 would wrongly emit two_side/both.
3. **Direction anomaly (36)**: source distance POSITIVE but GT bbox shows -Z body. v0.5 `direction_verified` cross-check catches this; v0.4 sign-based logic fails.
4. **arbitrary_closed generic dims (37)**: v0.5 NEW `arc_radii`/`line_lengths`/`circle_radii` capture all curves without type-specific recognition. v0.4 arbitrary_closed had no dimension extraction.
5. **Implicit concentricity (36)**: 2 CoincidentConstraints (no explicit Concentric) → concentric inferred. v0.4 only handled explicit.
6. **center_uv (33,34,35)**: v0.5 NEW circle center in part-local UV; captures offset positions without leaking world coords.
7. **EqualConstraint (38)**: 2 holes equal radius; v0.5 constraints enum += equal.
8. **Symmetric about plane intent (32)**: v0.5 NEW `symmetric_about_plane` validates centroid on sketch plane.
