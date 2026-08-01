import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104283_e5646f96_0000\neg_03\iter_00/generated.step"

# Design Plan: extruded circle (disk)
# - Circle center at (-15.0, 10.0) in sketch plane
# - Radius = 12.5 mm
# - Extrude distance = 75.0 mm along +w direction
# - Frame: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
#   This means the sketch plane is YZ (normal along X)
#   w_dir = [1,0,0] means extrusion along +X

# Build on YZ plane (X is normal)
result = (
    cq.Workplane("YZ")
    .moveTo(-15.0, 10.0)
    .circle(12.5)
    .extrude(75.0)
)

exporters.export(result, OUT_STEP_PATH)
