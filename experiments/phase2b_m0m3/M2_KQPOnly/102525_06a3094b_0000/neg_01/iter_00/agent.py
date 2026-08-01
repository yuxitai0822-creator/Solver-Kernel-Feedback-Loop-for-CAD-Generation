import cadquery as cq
from cadquery import exporters

# Design Plan: SOIC-8 body
# Dimensions: length_u=3.9 mm, width_v=4.9 mm, extrude_distance=1.55 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# The rectangle is centered at origin in the sketch plane (XZ plane)
# Extrude along Y axis (w_dir) by 1.55 mm

# Build the rectangle on XZ plane (since v_dir is [0,0,-1], the sketch plane normal is Y)
# Rectangle dimensions: 3.9 mm along X (u_dir), 4.9 mm along Z (v_dir magnitude)
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(3.9, 4.9, centered=True)
    .extrude(1.55)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0000\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)