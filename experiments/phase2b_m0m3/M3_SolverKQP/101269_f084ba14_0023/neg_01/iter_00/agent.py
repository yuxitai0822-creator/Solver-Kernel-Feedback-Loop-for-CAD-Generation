import cadquery as cq
from cadquery import exporters
import math

# Design Plan: basic slat v1 (5)
# Extruded rectangle with dimensions:
#   length_u (X): 95.25 mm
#   width_v (Z): 571.5 mm
#   extrude_distance (Y): 19.05 mm
#
# Coordinate system:
#   u_dir = [1,0,0] (X)
#   v_dir = [0,0,-1] (Z, negative)
#   w_dir = [0,1,0] (Y)
#
# The rectangle is defined in UV space with corners at:
#   (0,0), (9.525, 0), (9.525, 57.15), (0, 57.15)
# These are in UV coordinates where U maps to X and V maps to Z.
# The actual dimensions are:
#   U span = 9.525 * 10 = 95.25 mm (scaled by 10 from cm to mm)
#   V span = 57.15 * 10 = 571.5 mm
#
# The rectangle is drawn on the XZ plane (Y=0) and extruded in +Y direction by 19.05 mm.

# Build the rectangle on the XZ plane
result = (
    cq.Workplane("XZ")
    .center(95.25/2, 571.5/2)  # center at (47.625, 285.75)
    .rect(95.25, 571.5, centered=True)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101269_f084ba14_0023\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
