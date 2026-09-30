import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102760_26430589_0037\neg_03\iter_00/generated.step"

# Design Plan: single disk (extruded circle)
# - Circle radius: 0.8 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 4.0 mm (from dimensions.extrude_distance)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means the sketch plane is XZ (u=x, v=-z), extrude along w=y
# - No inner holes (only one outer ring, no inner rings in profiles)

# Build the disk
result = (
    cq.Workplane("XZ")  # sketch plane: XZ (u=x, v=-z)
    .circle(0.8)        # radius 0.8 mm
    .extrude(4.0)       # extrude 4.0 mm along Y (w direction)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
