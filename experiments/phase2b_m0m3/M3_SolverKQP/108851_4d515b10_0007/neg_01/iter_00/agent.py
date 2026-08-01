import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterBackBar1 v1
# Extruded rectangle: 279.4 mm x 50.8 mm, extrude 19.05 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Rectangle in UV plane: start (0,5.08) -> (0,0) -> (27.94,0) -> (27.94,5.08) -> close
# Note: UV coordinates are in cm in design plan, but unit is mm after conversion (x10)
# Actually the design plan says unit=mm, but compiler notes say cm_to_mm (x10)
# The rectangle dimensions: length_u=279.4 mm, width_v=50.8 mm
# The profile curves show start_uv/end_uv values that are 1/10 of actual dimensions
# because they were stored in cm. So we multiply by 10.
# Rectangle corners in mm: (0, 50.8), (0, 0), (279.4, 0), (279.4, 50.8)

# Build the rectangle on XZ plane (since v_dir is [0,0,-1], w_dir is [0,1,0])
# The sketch plane normal is w_dir = [0,1,0], so we use XZ plane

result = (
    cq.Workplane("XZ")
    .moveTo(0, 50.8)  # start at top-left
    .lineTo(0, 0)     # left edge down
    .lineTo(279.4, 0) # bottom edge right
    .lineTo(279.4, 50.8) # right edge up
    .close()          # top edge back to start
    .extrude(19.05)   # extrude along Y (w_dir = [0,1,0])
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108851_4d515b10_0007\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)