import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism with dimensions 3.9 x 4.9 x 1.55 mm
# The profile is a rectangle centered at origin, extruded along +w direction.
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the sketch plane is XZ (since u=x, v=-z, w=y).
# Rectangle half-lengths: u half = 3.9/2 = 1.95, v half = 4.9/2 = 2.45
# Extrude distance = 1.55 mm along +w (positive y direction).

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(3.9, 4.9, centered=True)
    .extrude(1.55)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0000\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)