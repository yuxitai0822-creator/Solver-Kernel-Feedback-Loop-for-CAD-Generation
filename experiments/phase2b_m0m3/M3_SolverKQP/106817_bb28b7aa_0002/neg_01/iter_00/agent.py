import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0002\neg_01\iter_00\generated.step"

# Design Plan parameters:
# - Circle center in UV: (11.430000364780426, 0.0) but the profile radius is 4.87045
# - The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# - Extrude distance = 6.8707 mm (the perturbed value 10.30605 is from cm conversion, but design plan says 6.8707)
# - The circle center in the profile is given as (11.430000364780426, 0.0) but the radius is 0.48704499999999984
#   However, the dimensions section says radius = 4.87045 and center_uv = [114.300004, 0.0]
#   The compiler notes say unit conversion cm_to_mm (x10), so the actual radius is 4.87045 mm
#   The center in the profile is (11.43, 0.0) which after x10 becomes (114.3, 0.0) — consistent.
#   But the profile ring has radius 0.48704499999999984 which is 10x smaller — this is likely a bug in the design plan.
#   We use the dimensions section: radius = 4.87045 mm, center = (114.300004, 0.0) in UV space.
#   However, the frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
#   So in 3D: u maps to X, v maps to -Z, w maps to Y.
#   The circle center in 3D: (114.300004, 0, 0) in (X, Y, Z) because u=114.3 -> X, v=0 -> Z=0, Y=0 from w=0.
#   But wait: the frame origin is at bbox_min_corner, so we need to place the circle appropriately.
#   For simplicity, we create the circle on the XZ plane (since v_dir = -Z, the sketch plane is XZ)
#   and extrude along Y (w_dir).

# Build the result
result = (
    cq.Workplane("XZ")
    .moveTo(114.300004, 0.0)
    .circle(4.87045)
    .extrude(6.8707)
)

exporters.export(result, OUT_STEP_PATH)
