import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Circle center in UV: (11.430000364780426, 0.0) - but the profile center_uv is (114.300004, 0.0)
# The radius from dimensions is 4.87045 mm (but the perturbed radius is 0.6088062499999998?)
# Actually looking at the design plan more carefully:
#   - profiles[0].rings[0].curves[0].center_uv = [11.430000364780426, 0.0]
#   - profiles[0].rings[0].curves[0].radius = 0.48704499999999984 (original, but perturbed to 0.6088062499999998)
#   - dimensions.profiles[0].radius = 4.87045 (this is the actual disk radius)
#   - dimensions.profiles[0].center_uv = [114.300004, 0.0]
#
# The disk radius is 4.87045 mm, extrude distance is 6.8707 mm
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So the sketch plane is XZ (u=x, v=-z), extrude along w=y

DISK_RADIUS = 4.87045  # mm
EXTRUDE_DISTANCE = 6.8707  # mm

# Build the disk centered at origin on XZ plane, extruded along Y
result = (
    cq.Workplane("XZ")
    .circle(DISK_RADIUS)
    .extrude(EXTRUDE_DISTANCE)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0002\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
