# Design Plan v0.2 Samples

These 5 Design Plans use the **v0.2 schema** (`DesignPlan/DesignPlan_schema02.txt`),
which addresses the weaknesses found in the v0.1 hand-written samples (see
`../` for v0.1 samples and `../../doc/03_DesignPlan_schema_v1评审与v2改进.md`).

## What changed from v0.1 → v0.2

| Aspect | v0.1 | v0.2 |
|---|---|---|
| Body structure | `base_geometry` + `features` (implicit ordering) | Single `solid_bodies[]` with `extrude` as a body property (no ordering) |
| Coordinate frame | `axis: "z"` string | Explicit `u_dir`/`v_dir`/`w_dir` unit vectors |
| Dimensions | `width_x`/`depth_y`/`height_z` tied to world axes | `along_u`/`along_v`/`along_w` tied to body frame |
| Envelope | `global_envelope.bbox` (GT copy) | `derived.design_envelope` (explicitly marked derived, not authoritative) |
| Provenance | No tracking | `source` field per dimension (`explicit_dimension` vs `inferred_from_point_span`) |
| Validation | Hardcoded intents | Auto-generated from `solid_bodies` dimensions |

## Sample-by-sample notes

| File | Key learning |
|---|---|
| `100243_9fb796fe_0005` | Clean baseline; 2 explicit dims, axis-aligned (XZ plane) |
| `100243_9fb796fe_0006` | Same profile family, shorter extrude; tests parametric consistency |
| `100877_ac1e5a17_0001` | Has CoincidentConstraint → compiler must recognize it as geometrically inert |
| `100877_ac1e5a17_0017` | Non-zero sketch plane origin → compiler must NOT copy offset into frame.origin |
| `101269_f084ba14_0023` | **Under-constrained**: only 1/2 dims explicit; tests point-span back-fill |

## Critical test case: sample 5

Sample `101269_f084ba14_0023` exposes the single most important compiler
requirement: **a dimensions-only compiler fails here**. The source has only
`d1_18=9.525` (Horizontal); the 57.15mm length has no driving dimension and
must be reconstructed from sketch point coordinates. The v0.2 plan captures
this via `source: "inferred_from_point_span"` and a `warnings` entry.
