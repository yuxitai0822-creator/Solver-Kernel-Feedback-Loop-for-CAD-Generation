import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0002\neg_03\iter_00/generated.step"

# Design parameters from the design plan
# The profile is a circle with radius 4.87045 mm, centered at (11.43, 0.0) in UV space
# The extrude distance is 6.8707 mm along +w direction
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means the sketch plane is XZ (u=x, v=-z), and extrusion is along +w = +y

radius = 4.87045
center_u = 11.430000364780426
center_v = 0.0
extrude_distance = 6.8707

# Build the part
# Workplane XZ matches the frame: u=x, v=-z (but we use XZ which is x,z)
# The center is at (center_u, center_v) in UV = (x, -z) in world
# So we move to (center_u, -center_v) = (11.43, 0.0) on XZ plane
result = (
    cq.Workplane("XZ")
    .moveTo(center_u, -center_v)  # v_dir = [0,0,-1], so v coordinate maps to -z
    .circle(radius)
    .extrude(extrude_distance)  # extrude along +w = +y
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")