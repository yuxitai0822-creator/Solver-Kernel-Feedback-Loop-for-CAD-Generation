import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0000\neg_02\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 40mm x 40mm (in UV plane)
# Inner rectangle: 37.6mm x 37.6mm (wall thickness ~1.2mm)
# Extrude distance: 780mm along W direction (Y axis)
# The UV coordinates from the plan are:
#   Outer: u in [6.0, 10.0], v in [-7.0, -3.0]  -> span 4.0 in both u and v
#   Inner: u in [6.12, 9.88], v in [-6.88, -3.12] -> span 3.76 in both u and v
# But the dimensions say outer_length_u=40.0, outer_width_v=40.0, inner_length_u=37.6, inner_width_v=37.6
# This means the UV coordinates are scaled by 10 (since 4.0*10=40, 3.76*10=37.6)
# So we build the profile in mm directly using the dimension values.

# Build the outer rectangle centered at origin
outer_w = 40.0
outer_h = 40.0
inner_w = 37.6
inner_h = 37.6
extrude_dist = 780.0

# Create workplane on XZ plane (since normal is Y axis = [0,1,0])
# The frame's u_dir = [1,0,0] (X), v_dir = [0,0,-1] (negative Z), w_dir = [0,1,0] (Y)
# So sketch on XZ plane, extrude along Y
wp = cq.Workplane("XZ")

# Draw outer rectangle centered at origin
wp = wp.center(0, 0).rect(outer_w, outer_h)

# Draw inner rectangle as a hole (centered)
wp = wp.center(0, 0).rect(inner_w, inner_h, forConstruction=True)

# Extrude to create the hollow box
result = wp.extrude(extrude_dist)

# Export
importers = cq.exporters
exporters.export(result, OUT_STEP_PATH)
