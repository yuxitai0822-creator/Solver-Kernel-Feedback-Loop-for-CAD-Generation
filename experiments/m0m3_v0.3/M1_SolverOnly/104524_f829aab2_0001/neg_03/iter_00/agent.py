import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104524_f829aab2_0001\neg_03\iter_00\generated.step"

# Design Plan: single disk (extruded circle)
# - Circle radius: 7.5 mm (from dimensions.profiles[0].radius.value = 7.5)
# - Extrude distance: 20.0 mm (from extrude.distance_total.value = 20.0)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means sketch plane is XZ (u=x, v=z), extrude along +w = +y
# - No inner loops (the previous script incorrectly added an inner loop of radius 0.5)
# - Body count: 1
# - Validation: span_u=15.0, span_v=15.0, span_w=20.0 (diameter=15, height=20)

# Build the disk
result = (
    cq.Workplane("XZ")  # sketch plane: u=x, v=z
    .circle(7.5)         # radius 7.5 mm
    .extrude(20.0)       # extrude along +y (w direction) by 20 mm
)

# Export STEP
exporters.export(result, OUT_STEP_PATH)
