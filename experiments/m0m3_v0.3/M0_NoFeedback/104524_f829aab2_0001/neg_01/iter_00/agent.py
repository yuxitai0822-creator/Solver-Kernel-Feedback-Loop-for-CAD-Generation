import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104524_f829aab2_0001\neg_01\iter_00\generated.step"

# Design Plan: extruded circle (disk)
# - Circle radius: 7.5 mm (from dimensions.profiles[0].radius.value = 7.5)
# - Extrude distance: 20.0 mm (from dimensions.extrude_distance.value = 20.0)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means sketch plane is XZ (u=x, v=-z), extrude along +w = +y

# Build on XZ plane (normal = Y axis)
result = (
    cq.Workplane("XZ")
    .circle(7.5)  # radius in mm
    .extrude(20.0)  # extrude along Y (positive w direction)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
