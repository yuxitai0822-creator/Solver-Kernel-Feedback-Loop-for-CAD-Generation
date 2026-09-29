# Design Plan v0.4 Samples (21-30)

These 10 Design Plans use the **v0.4 schema** (`DesignPlan/DesignPlan_schema04.txt`),
which addresses v0.3 weaknesses found when samples 21-30 introduced negative
extrusion, multi-profile single extrude, rectangular frames, and dimension-less
circles (see `../../doc/DesignPlan_schema_v3评审与v4改进.md`).

## Sample inventory

| # | File | Profile type | Key challenge |
|---|---|---|---|
| 21 | `102760_26430589_0037` | circle | **Negative extrude** (distance=-0.4cm → direction=-w, magnitude=4mm) |
| 22 | `103284_e25015aa_0003` | circle + unused sketch | Multi-sketch; Sketch5 unconsumed; offset circle center |
| 23 | `103284_e25015aa_0004` | circle | Offset center; 0 constraints |
| 24 | `103481_b27a1cdf_0010` | rectangle (square) | Construction diagonals; 45° principal axes artifact |
| 25 | `103552_c3a389ed_0003` | stadium + 2 holes | Concentric holes with end arcs; construction centerline |
| 26 | `104283_e5646f96_0000` | circle (YZ plane) | YZ plane orientation; heavily offset origin |
| 27 | `104283_e5646f96_0001` | **multi-profile** | 2 profiles in 1 extrude (rect + circle-with-rect-hole), unioned |
| 28 | `104453_aba0f2d1_0002` | stadium (large) | d1_3 "Vertical" = 2*radius (not edge length) |
| 29 | `104453_aba0f2d1_0006` | **rectangular_frame** | Outer rect + inner rect hole (8 curves, 2 loops) |
| 30 | `104524_f829aab2_0001` | circle | **No dimension** (radius from curve_field only) |

## Key findings encoded in these samples

1. **Negative extrude (21)**: `extrude.direction="-w"` + `distance_total=4.0` (magnitude). Decouples sign from magnitude.
2. **Multi-profile single extrude (27)**: `profiles[]` (plural) with 2 entries. v0.3 single-profile structure cannot represent this.
3. **Rectangular frame (29)**: new `profile.type=rectangular_frame` with outer/inner rectangle params.
4. **Dimension-less circle (30)**: `source="curve_field"` (3rd source type, beyond explicit_dimension/inferred_from_point_span).
5. **YZ plane (26)**: 3rd base plane orientation tested (after XY/XZ).
6. **Stadium dimension labeling (28)**: "Vertical" dimension on a stadium = 2*radius, not an edge length. Compiler must halve.
7. **Multi-sketch with unused (22)**: Sketch5 (concentric circles) unconsumed → auxiliary_geometry.
8. **Construction curve filtering (24, 25)**: sketch has extra construction lines/arcs beyond profile boundary; compiler must use profile.loops to extract true boundary curves.
