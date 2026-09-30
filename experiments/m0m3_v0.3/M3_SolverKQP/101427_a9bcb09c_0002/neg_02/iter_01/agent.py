import cadquery as cq
from cadquery import exporters

# Design Plan: flat plate/panel, extruded rectangle
# Dimensions: length_u=1930.0 mm, width_v=550.0 mm, extrude_distance=50.0 mm
# Note: The design plan specifies dimensions in mm (converted from cm: x10)
# The profile curves show u range [0, 193] and v range [0, 55] in cm, so in mm: u=1930, v=550
# Extrude direction is +w (which maps to +Y in world coordinates per frame definition)

# Build the rectangle on the XZ plane (since w_dir = [0,1,0] means extrusion along Y)
# The profile is in uv space where u -> X, v -> Z (since v_dir = [0,0,-1])
# Rectangle: width=1930 along X, height=550 along Z
result = (
    cq.Workplane("XZ")
    .center(1930.0/2, 550.0/2)  # center at midpoint for rect()
    .rect(1930.0, 550.0)
    .extrude(50.0)  # extrude along Y (positive direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0002\neg_02\iter_01/generated.step"
exporters.export(result, OUT_STEP_PATH)