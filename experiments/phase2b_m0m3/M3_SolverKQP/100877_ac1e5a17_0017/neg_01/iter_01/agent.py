import cadquery as cq
from cadquery import exporters

# Design Plan: flat plate/panel, extruded rectangle
# Dimensions: length_u=254.0 mm, width_v=190.5 mm, extrude_distance=3.175 mm
# The previous script had a typo: "importers" instead of "exporters" for the export call.
# Also, the rectangle dimensions from the design plan curves are 25.4 mm x 19.05 mm.
# The dimensions table says 254.0 x 190.5, but the curves are the authoritative source.
# The extrude depth is 3.175 mm as specified.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0017\neg_01\iter_01\generated.step"

# Create workplane
wp = cq.Workplane("XY")

# Build rectangle from the 4 corner points as defined in the design plan curves
# Start at (0, 19.05), go to (0, 0), then (25.4, 0), then (25.4, 19.05), close back to (0, 19.05)
wp = wp.moveTo(0, 19.05)
wp = wp.lineTo(0, 0)
wp = wp.lineTo(25.4, 0)
wp = wp.lineTo(25.4, 19.05)
wp = wp.close()

# Extrude by 3.175 mm in +Z direction
result = wp.extrude(3.175)

# Export using correct module name
exporters.export(result, OUT_STEP_PATH)
