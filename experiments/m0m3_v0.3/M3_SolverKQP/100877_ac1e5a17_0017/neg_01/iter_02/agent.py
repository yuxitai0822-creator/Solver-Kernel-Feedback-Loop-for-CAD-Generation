import cadquery as cq
from cadquery import exporters

# Design Plan: flat plate/panel, extruded rectangle
# Dimensions: length_u=254.0 mm, width_v=190.5 mm, extrude_distance=3.175 mm
# The previous script used 25.4 x 19.05 mm for the rectangle, but the design plan's
# dimensions table specifies 254.0 x 190.5 mm. The curves in the design plan are
# in cm (2.54 x 1.905 cm) which convert to 25.4 x 19.05 mm, but the explicit
# dimensions table overrides this with 254.0 x 190.5 mm. We use the explicit dimensions.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0017\neg_01\iter_02\generated.step"

# Create workplane
wp = cq.Workplane("XY")

# Build rectangle using the explicit dimensions from the design plan
# length_u = 254.0 mm, width_v = 190.5 mm
# Center the rectangle at the origin for simplicity
wp = wp.rect(254.0, 190.5, centered=True)

# Extrude by 3.175 mm in +Z direction
result = wp.extrude(3.175)

# Export
importers.export(result, OUT_STEP_PATH)