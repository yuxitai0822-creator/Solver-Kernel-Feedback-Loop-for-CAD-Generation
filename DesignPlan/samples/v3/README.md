# Design Plan v0.3 Samples (11-20)

These 10 Design Plans use the **v0.3 schema** (`DesignPlan/DesignPlan_schema03.txt`),
which addresses the v0.2 weaknesses found when samples 6-20 introduced curved
surfaces, annuli, multi-sketch timelines, and rotated frames
(see `../../doc/DesignPlan_schema_v2评审与v3改进.md`).

## Sample inventory

| # | File | Profile type | Key challenge |
|---|---|---|---|
| 11 | `101817_b02acd9f_0004` | rectangle | Large flat panel (1200×600×20mm); baseline rect |
| 12 | `102175_699d5e7c_0003` | rectangle | Small block; CoincidentConstraint inert handling |
| 13 | `102295_86f842dd_0000` | **stadium** | First curved profile (2 arcs + 2 lines); Tangent constraints; u_dir label mismatch |
| 14 | `102314_91648bfc_0000` | **annulus** | Multi-sketch timeline (unused Sketch2); Concentric; Euler anomaly |
| 15 | `102369_65e5a7e6_0003` | **polygon_with_fillets** | Triangle + 2 fillets + 2 holes (3 rings); 8 dimensions, 4 positioning |
| 16 | `102410_f9877a7b_0000` | annulus | Concentricity via 2 CoincidentConstraints (implicit) |
| 17 | `102410_f9877a7b_0012` | annulus | Concentricity via explicit ConcentricConstraint (contrast w/ 16) |
| 18 | `102525_06a3094b_0000` | rectangle | Flipped frame u=(0,0,-1), v=(-1,0,0); construction diagonals |
| 19 | `102525_06a3094b_0004` | rectangle | Flipped frame; borderline part_category |
| 20 | `102525_06a3094b_0006` | rectangle | **Rotated frame** (~0.28deg); critical vertex_projection test |

## Key findings encoded in these samples

1. **Curved profiles (13, 15)**: v0.3 `profile.type=stadium/polygon_with_fillets` + parametric `dimensions` (radius, side_lengths, fillet_radii, hole_radii) capture what v0.2's 3-axis model could not.

2. **Multi-ring profiles (14, 15, 16, 17)**: `profile.rings[]` with `role=outer/inner` expresses holes/annuli that v0.2 had no structure for.

3. **Multi-sketch timelines (14)**: `auxiliary_geometry.unused_sketches` isolates Sketch2 (positioning reference) from `solid_bodies`.

4. **Frame orientation edge cases (18, 19, 20)**: flipped (negated) and rotated (non-axis-aligned) frames. `span_computation=vertex_projection` is mandatory; axis-aligned bbox fails for sample 20.

5. **Concentricity dual encoding (16 vs 17)**: same geometry, but 16 expresses concentricity via 2 CoincidentConstraints (implicit) while 17 uses explicit ConcentricConstraint. Compiler must recognize both.

6. **Unit conversion (all)**: every sample applies cm→mm (×10). Documented in `compiler_notes.unit_conversion_applied` + per-sample warnings.

7. **u_dir label vs actual mapping (13, 18, 19, 20)**: `reference_plane.u_direction` does NOT always match the sketch-point→world mapping (corrective_transform implied). Compiler MUST derive dimensions from point spans, not u_direction labels.
