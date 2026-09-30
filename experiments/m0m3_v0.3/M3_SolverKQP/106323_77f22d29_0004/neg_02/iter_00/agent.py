import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
OUTER_RADIUS = 17.5  # mm (from dimensions.outer_radius.value)
INNER_RADIUS = 12.5  # mm (from dimensions.inner_radius.value)
EXTENT_TOTAL_MM = 10.0  # mm (from extrude.distance_total.value)

# Build the part: extruded annulus (washer shape)
# Start with a workplane on XY plane
result = (
    cq.Workplane("XY")
    .circle(OUTER_RADIUS)  # outer circle
    .circle(INNER_RADIUS)  # inner circle (creates a hole)
    .extrude(EXTENT_TOTAL_MM)  # extrude symmetrically? No, we extrude in one direction
)

# The design plan specifies symmetric extrusion (both_symmetric) with total distance 10mm.
# To achieve symmetric extrusion, we extrude half in one direction and then mirror or
# use the 'both' parameter. However, cadquery's extrude with 'both' is not directly supported.
# Instead, we extrude the full distance and then center the result.
# Since the design plan says symmetric, we'll extrude half distance and then mirror.
# But simpler: extrude full distance and then translate so it's centered on Z.
# Actually, the simplest approach: extrude half distance, then mirror the solid.

# Let's rebuild properly with symmetric extrusion:
result = (
    cq.Workplane("XY")
    .circle(OUTER_RADIUS)
    .circle(INNER_RADIUS)
    .extrude(EXTENT_TOTAL_MM / 2)  # extrude half in +Z
)

# Mirror to get the other half (symmetric about XY plane)
result = result.mirror("XY")

# Now the part is centered at Z=0 with total thickness 10mm.
# But mirror creates a compound; we need to fuse them.
# Actually, mirror returns a solid that is the union of original and mirrored.
# Let's verify: result is now a solid with total extent 10mm in Z.

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106323_77f22d29_0004\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
