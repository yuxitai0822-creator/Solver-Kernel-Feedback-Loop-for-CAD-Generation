import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism with dimensions 11.3 x 21.0 x 3.0 mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Profile rectangle centered at origin in UV plane, with half-lengths:
#   u half-length = 11.3/2 = 5.65
#   v half-length = 21.0/2 = 10.5
# Extrude along +w (y-axis) by 3.0 mm

# Build on XY plane, then rotate to match frame: w_dir = (0,1,0) means extrusion along Y.
# We'll create the rectangle on XZ plane (since v_dir = (0,0,-1) is along Z negative, but we can just use XZ and extrude along Y).
# Simpler: use Workplane("XZ") so that the sketch plane normal is Y (which is w_dir).
# On XZ plane, u = X, v = Z (but v_dir is (0,0,-1), so we need to flip Z sign).
# To match exactly: rectangle centered at (0,0) with width=11.3 (along X) and height=21.0 (along Z).
# Then extrude in +Y direction by 3.0.

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(11.3, 21.0, centered=True)
    .extrude(3.0)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102525_06a3094b_0006\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)