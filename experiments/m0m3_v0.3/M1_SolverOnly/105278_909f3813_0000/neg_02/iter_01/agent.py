import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism 12mm x 60mm x 40mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from -0.6 to 0.6, v from -3.0 to 3.0
# Extrude 40mm in +w direction

# Build on XY plane, then rotate to match frame orientation
# Frame: u=x, v=-z, w=y
# So sketch on XZ plane (u=x, v=-z) then extrude in +y (w)

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(1.2, 6.0, centered=True)  # width=1.2 (u), height=6.0 (v)
    .extrude(40.0)  # extrude in +y (w direction)
)

exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\105278_909f3813_0000\neg_02\iter_01/generated.step")
