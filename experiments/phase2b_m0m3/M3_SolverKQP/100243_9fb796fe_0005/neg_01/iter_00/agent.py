import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Drone Leg Left - square strut
# Extruded rectangle with dimensions 19mm x 19mm x 200mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane, extrude along +w (Y axis)

# Profile rectangle corners in UV coordinates (from design plan curves):
# u range: [-58.27820137826746, -56.37820137826746] -> width = 1.9 (but should be 19mm after cm->mm conversion?)
# v range: [-13.940145769681571, -12.04014576968157] -> height = 1.9
# Wait - the design plan says length_u=19.0, width_v=19.0, extrude_distance=200.0
# The UV coordinates given are in cm (since compiler notes say cm_to_mm x10)
# So UV coords in cm: width = 1.9cm = 19mm, height = 1.9cm = 19mm
# But the actual values: -56.378 - (-58.278) = 1.9, and -12.040 - (-13.940) = 1.9
# So these are in cm, need to multiply by 10 to get mm

# Let's build directly from the design plan dimensions:
# Rectangle: 19mm x 19mm, extrude 200mm along Y axis
# Center the rectangle at origin in XZ plane, extrude along Y

# Create workplane on XZ plane (since w_dir = [0,1,0] = Y axis)
# The profile is in UV plane where U=X, V=Z (since v_dir = [0,0,-1] means V is -Z)
# Actually: u_dir=[1,0,0]=X, v_dir=[0,0,-1]=-Z, w_dir=[0,1,0]=Y
# So the sketch plane is XZ (with V reversed), extrude along Y

# Build the rectangle centered at origin
result = (
    cq.Workplane("XZ")
    .rect(19.0, 19.0, centered=True)
    .extrude(200.0)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0005\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
