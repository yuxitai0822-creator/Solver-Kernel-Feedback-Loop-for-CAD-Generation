import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102760_26430589_0037\neg_02\iter_00\generated.step"

# Design Plan: extruded circle (disk)
# - Circle radius: 0.8 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance: 4.0 mm (from dimensions.extrude_distance.value)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means the sketch plane is XZ (u=x, v=z), extrude along w=y
# - The perturbed radius from the history JSON is 1.0, but the design plan says 0.8
#   We follow the design plan dimensions explicitly.

# Create workplane on XZ plane (since u=x, v=z)
wp = cq.Workplane("XZ")

# Draw circle with radius 0.8 mm at origin
circle = wp.circle(0.8)

# Extrude along Y direction (w_dir = [0,1,0]) by 4.0 mm
# Since we're on XZ plane, extrude in +Y direction
result = circle.extrude(4.0)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
