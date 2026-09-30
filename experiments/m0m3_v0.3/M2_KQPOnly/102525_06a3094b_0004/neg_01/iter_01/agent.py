import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin in the XY plane
# Extrude in +Z direction by 2.5 mm
# Note: The design plan's frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means u corresponds to X, v corresponds to -Z, w corresponds to Y.
# So the rectangle dimensions: length_u = 8.5 (X), width_v = 18.0 (Z), extrude distance = 2.5 (Y)
# To match the expected bbox sizes: X=8.5, Y=2.5, Z=18.0

# Build the rectangle profile on the XZ plane (since v is along -Z, we use XZ plane)
# The rectangle is centered at origin, with width along X = 8.5, height along Z = 18.0
result = (
    cq.Workplane("XZ")
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)  # extrude along Y (normal of XZ plane)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0004\neg_01\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)