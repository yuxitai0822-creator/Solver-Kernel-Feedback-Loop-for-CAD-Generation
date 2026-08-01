import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104524_f829aab2_0001\neg_02\iter_00/generated.step"

# Design Plan parameters:
# - Disk (extruded circle)
# - Radius = 7.5 mm (from dimensions.profiles[0].radius)
# - Extrude distance = 20.0 mm (from dimensions.extrude_distance)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means the sketch plane is XZ (u=x, v=z), extrude along +w = +y

radius = 7.5
extrude_height = 20.0

# Build the disk: circle on XZ plane, extrude along Y axis
result = (
    cq.Workplane("XZ")
    .circle(radius)
    .extrude(extrude_height)
)

# Export to STEP
importers = None
exporters.export(result, OUT_STEP_PATH)
