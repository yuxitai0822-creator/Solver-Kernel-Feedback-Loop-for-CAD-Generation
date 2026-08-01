import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102175_699d5e7c_0003\neg_03\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 39.0 x 68.0 x 10.0 mm
# The profile is a rectangle in the XY plane, extruded in +Z direction.
# The rectangle corners in UV coordinates (from design plan):
#   (-3.9, 6.8) -> (0.0, 6.8) -> (0.0, 0.0) -> (-3.9, 0.0)
# Note: The design plan states unit conversion cm->mm (x10), so the actual dimensions are:
#   length_u = 39.0 mm (from -3.9 to 0.0 in U, times 10)
#   width_v = 68.0 mm (from 0.0 to 6.8 in V, times 10)
#   extrude_distance = 10.0 mm
# The rectangle is centered at (-1.95, 3.4) in UV space, which after scaling becomes (-19.5, 34.0) in mm.

# Build the rectangle centered at the origin for simplicity, then translate if needed.
# The design plan's coordinate system has origin at bbox_min_corner, so we place the rectangle
# such that its min corner is at (0,0) in the local frame.
# After scaling: width = 39.0 mm, height = 68.0 mm, extrude = 10.0 mm.

result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0, centered=False)
    .extrude(10.0)
)

exporters.export(result, OUT_STEP_PATH)
