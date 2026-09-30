import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104283_e5646f96_0000\neg_02\iter_00\generated.step"

# Design Plan parameters:
# - Circle center in UV: (-15.0, 10.0) -> but note: the frame has u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
#   This means the sketch plane is YZ (since w_dir is X axis, extrusion along X).
#   In the sketch plane (YZ), u corresponds to -Z, v corresponds to Y.
#   So center_uv = (-15.0, 10.0) means center at (Y=10, Z=-(-15)=15) in YZ plane.
# - Radius = 12.5 mm (from dimensions.radius.value)
# - Extrude distance = 75.0 mm along +w direction (which is +X)

# Build the part:
# Workplane on YZ (since extrusion is along X)
result = (cq.Workplane("YZ")
          .circle(12.5)
          .extrude(75.0))

# The circle is centered at (0,0) in the YZ plane by default.
# We need to move it to center (Y=10, Z=15) as per the design plan.
# Let's rebuild with proper positioning:
result = (cq.Workplane("YZ")
          .center(10.0, 15.0)  # Y=10, Z=15
          .circle(12.5)
          .extrude(75.0))

exporters.export(result, OUT_STEP_PATH)
