import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u = 209.55 mm, width_v = 57.912 mm, extrude_distance = 19.05 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# The rectangle is in the uv-plane, extruded along +w (y-axis)

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1], u is x, v is z)
# The rectangle spans from (0,0) to (209.55, 57.912) in uv coordinates
# In world: u -> x, v -> z (but v_dir is [0,0,-1], so v coordinate maps to -z)
# To keep it simple: create rectangle on XZ plane, then extrude along Y

result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912, centered=False)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108851_4d515b10_0009\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)