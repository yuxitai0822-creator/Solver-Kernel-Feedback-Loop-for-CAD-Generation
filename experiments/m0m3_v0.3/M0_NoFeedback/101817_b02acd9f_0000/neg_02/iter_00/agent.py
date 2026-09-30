import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0000\neg_02\iter_00\generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 40mm x 40mm (in UV plane)
# Inner rectangle: 37.6mm x 37.6mm (wall thickness 1.2mm)
# Extrude distance: 780mm along W direction (Y axis)
# The frame uses coordinate system: U=X, V=-Z, W=Y
# So we sketch on XZ plane, extrude along Y

# Outer rectangle dimensions (mm)
outer_u = 40.0  # along X
outer_v = 40.0  # along Z (but we use positive Z for sketch)
inner_u = 37.6
inner_v = 37.6

# Extrude distance along Y (W direction)
extrude_dist = 780.0

# Build the hollow box using CadQuery
# Start with a box for the outer shape, then subtract the inner cavity

# Outer box: centered at origin, dimensions: outer_u x extrude_dist x outer_v
result = (
    cq.Workplane("XY")
    .box(outer_u, extrude_dist, outer_v, centered=(True, True, True))
)

# Inner cavity: slightly smaller box to create hollow frame
# The cavity should be centered and have dimensions: inner_u x (extrude_dist - 2*wall) x inner_v
# But since we want a frame with uniform wall thickness, we subtract a box that is
# inner_u wide, inner_v tall, and extends the full length (extrude_dist)
# This creates a through-hole along the Y axis

inner_cavity = (
    cq.Workplane("XY")
    .box(inner_u, extrude_dist * 1.1, inner_v, centered=(True, True, True))
)

result = result.cut(inner_cavity)

# Export the result
exporters.export(result, OUT_STEP_PATH)
