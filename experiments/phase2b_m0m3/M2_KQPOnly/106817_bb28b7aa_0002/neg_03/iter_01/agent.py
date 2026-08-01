import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0002\neg_03\iter_01/generated.step"

# Design Plan parameters:
# - Circle center in UV: (11.430000364780426, 0.0) but note the profile center_uv is (114.300004, 0.0) after scaling?
#   Actually the design plan says: center_uv = [11.430000364780426, 0.0] for the ring, but dimensions say center_uv = [114.300004, 0.0].
#   The compiler note says unit conversion cm->mm (x10). So the original was in cm: 11.43 cm = 114.3 mm. So we use 114.300004 mm.
# - Radius: 4.87045 mm (from dimensions)
# - Extrude distance: 6.8707 mm
# - The frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0). So the sketch plane is XZ (u=x, v=z), extrude along w=y.
# - The circle center in sketch coordinates (u,v) = (114.300004, 0.0).
# - No inner hole (the previous script had an inner loop of radius 0.5, but the design plan shows only one outer ring, no inner ring).
#   The perturbation description says "operator=E4_void_add; original=0; perturbed=1" meaning an extra void was added.
#   We must follow the design plan: only one circle, no hole.

# Build the part:
# Workplane on XZ (since u=x, v=z).
wp = cq.Workplane("XZ")

# Move to center and create circle
center_u = 114.300004
center_v = 0.0
radius = 4.87045

# Create the circle on the workplane
circle_wp = wp.moveTo(center_u, center_v).circle(radius)

# Extrude along the w direction (which is y-axis). The design says direction = +w, distance = 6.8707 mm.
extrude_distance = 6.8707
result = circle_wp.extrude(extrude_distance)

# Export
cq.exporters.export(result, OUT_STEP_PATH)