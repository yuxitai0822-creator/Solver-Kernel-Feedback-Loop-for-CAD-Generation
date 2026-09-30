import cadquery as cq
from cadquery import exporters

# Design Plan: SOIC-8 body
# Dimensions: length_u=3.9 mm, width_v=4.9 mm, extrude_distance=1.55 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in UV plane

# Build the rectangle profile in the XZ plane (since v_dir is [0,0,-1], w_dir is [0,1,0])
# The rectangle spans from -1.95 to 1.95 in u (X) and -2.45 to 2.45 in v (Z)
# Extrude along w (Y) direction by 1.55 mm

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(3.9, 4.9, centered=True)
    .extrude(1.55)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102525_06a3094b_0000\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)