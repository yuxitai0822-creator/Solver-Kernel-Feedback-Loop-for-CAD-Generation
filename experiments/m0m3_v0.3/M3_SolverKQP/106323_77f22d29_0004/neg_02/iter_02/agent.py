import cadquery as cq
from cadquery import exporters

# Design parameters from the design plan
OUTER_RADIUS = 17.5  # mm (from dimensions.outer_radius.value)
INNER_RADIUS = 12.5  # mm (from dimensions.inner_radius.value)
EXTENT_TOTAL_MM = 10.0  # mm (from extrude.distance_total.value)

# Build the part: extruded annulus (washer shape) with symmetric extrusion
# The design plan specifies symmetric extrusion (both_symmetric) with total distance 10mm.
# To achieve this, we extrude half the total distance in +Z, then mirror to get the other half.
# This ensures the part is centered at Z=0 with total thickness 10mm.

result = (
    cq.Workplane("XY")
    .circle(OUTER_RADIUS)  # outer circle
    .circle(INNER_RADIUS)  # inner circle (creates a hole)
    .extrude(EXTENT_TOTAL_MM / 2)  # extrude half in +Z
)

# Mirror to get the other half (symmetric about XY plane)
result = result.mirror("XY")

# The mirror operation creates a compound of two solids (original + mirrored).
# To get a single solid with total Z-span of 10mm, we need to fuse them.
result = result.fuse(result)  # fuse the compound into a single solid

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106323_77f22d29_0004\neg_02\iter_02\generated.step"
exporters.export(result, OUT_STEP_PATH)