import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame
# Outer rectangle: from (-2.5, 57.5) to (195.5, -2.5) in UV plane
#   -> width = 195.5 - (-2.5) = 198.0, height = 57.5 - (-2.5) = 60.0
# Inner rectangle: from (0.0, 55.0) to (193.0, 0.0)
#   -> width = 193.0, height = 55.0
# Extrude distance: 25.0 mm (from design plan, not the perturbed 37.5)
# Frame axes: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# So sketch on XZ plane, extrude along Y

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0001\neg_01\iter_02\generated.step"

# Build the outer rectangle
result = (cq.Workplane("XZ")
    .moveTo(-2.5, 57.5)
    .lineTo(-2.5, -2.5)
    .lineTo(195.5, -2.5)
    .lineTo(195.5, 57.5)
    .close()
    .extrude(25.0)  # extrude along Y (positive direction)
)

# Cut the inner hole
inner = (cq.Workplane("XZ")
    .moveTo(0.0, 55.0)
    .lineTo(0.0, 0.0)
    .lineTo(193.0, 0.0)
    .lineTo(193.0, 55.0)
    .close()
    .extrude(25.0)  # same extrusion depth
)

result = result.cut(inner)

exporters.export(result, OUT_STEP_PATH)