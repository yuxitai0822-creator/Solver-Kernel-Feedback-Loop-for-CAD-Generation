# Design Plan Samples (Hand-Written from Sanity Set)

These 5 Design Plans were hand-written by reading the modeling-history JSON of
the first 5 sanity samples, then applying the four quality criteria
(Sufficiency, Non-Procedurality, Verifiability, Non-Leakage) to extract a
result-level design spec.

## Samples

| File | Source Sample | Geometry | Notes |
|---|---|---|---|
| `100243_9fb796fe_0005.design_plan.json` | Drone Leg Left | 1.9×1.9×20 square strut | All 3 axes rectangular; clean case |
| `100243_9fb796fe_0006.design_plan.json` | Drone Leg | 1.9×1.9×13 square strut | Same family, shorter extrude |
| `100877_ac1e5a17_0001.design_plan.json` | Backing v1 | 27.94×21.59×0.159 plate | Has Coincident constraint; thin plate |
| `100877_ac1e5a17_0017.design_plan.json` | Image 1 v1 | 25.4×19.05×0.318 plate | Offset sketch plane origin (1.27,1.27,3.49) |
| `101269_f084ba14_0023.design_plan.json` | basic slat v1 (5) | 9.525×1.905×57.15 slat | **Under-constrained source** (only 1 of 2 dims) |

## Design Choices Applied

1. **Coordinate system**: switched to `part_local` with `origin_convention:
   bbox_min_corner`. The source's world coordinates (e.g., sample 1 sits at
   (-58.278, 0, 12.040) in assembly space) are assembly-context and are
   deliberately omitted (Non-Leakage).

2. **No procedural fields**: timeline order, sketch_id, profile_id, body UUIDs
   are all absent. The Design Plan says *what* to build, not *how*.

3. **No exact topology counts**: face_count, edge_count, vertex_count,
   volume, surface_area are NOT in the Design Plan (they're GT-side leak).
   They will be **derived** by the KQP compiler from the geometry spec, not
   asserted by the plan itself.

4. **Tolerances**: 0.01mm on structural dims, 0.005mm on thin-plate thickness,
   reflecting realistic CAD precision.

5. **Validation intents**: only include queries the KQP can directly verify
   against the STEP geometry — body_count, bbox_size, all_faces_planar,
   is_solid, occt_is_valid. Notably **volume is NOT a validation intent**
   (it's a derived consequence, not a design specification).

## Key Insight from Sample 5

Sample `101269_f084ba14_0023` is **under-constrained in its source JSON**:
only 1 of the 2 rectangle dimensions is an explicit driving dimension. The
second dimension (57.15mm) is implicit — it's encoded in the point
coordinates and the closed profile, but has no `SketchLinearDimension` entry.
This is a critical case for the deterministic compiler design: a naive
"copy all dimensions" compiler would silently drop the 57.15mm value.
