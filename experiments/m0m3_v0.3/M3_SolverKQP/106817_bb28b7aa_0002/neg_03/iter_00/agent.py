import cadquery as cq
from cadquery import exporters
import math

# Design Plan: thumb screw (disk)
# Body: extruded circle
#   Profile: circle, radius=4.87045 mm, center_uv=(11.430000364780426, 0.0)
#   Extrude: one_side, direction=+w, distance=6.8707 mm
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
#   => sketch on XZ plane, extrude along Y (positive)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0002\neg_03\iter_00/generated.step"

# Parameters from design plan
radius = 4.87045  # mm
extrude_distance = 6.8707  # mm
center_x = 11.430000364780426  # uv coordinate in sketch plane
center_y = 0.0

# Build the part
# Workplane: XZ (since v_dir = (0,0,-1) means sketch normal is -Z? Actually w_dir=(0,1,0) is extrusion direction)
# Let's use XY plane and then rotate? Simpler: use XZ plane directly.
# The frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# So sketch plane is defined by u and v axes: X and -Z => XZ plane
# Extrude along w = Y axis

result = (
    cq.Workplane("XZ")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(extrude_distance)
)

# Export
exporters.export(result, OUT_STEP_PATH)
