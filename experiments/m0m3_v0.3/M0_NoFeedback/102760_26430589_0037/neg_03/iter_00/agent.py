import cadquery as cq
from cadquery import exporters
import math

# Design Plan: single disk (extruded circle)
# - Circle radius: 0.8 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance: 4.0 mm (from dimensions.extrude_distance.value)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means sketch plane is XZ (u=x, v=z), extrude along w=y
# - No inner holes (only one outer ring, no inner rings)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102760_26430589_0037\neg_03\iter_00\generated.step"

# Build the disk
# Workplane XZ matches the frame: u=x, v=z, extrude along y (w_dir)
result = (
    cq.Workplane("XZ")
    .circle(0.8)  # radius from design plan
    .extrude(4.0)  # extrude distance along Y (positive direction)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
