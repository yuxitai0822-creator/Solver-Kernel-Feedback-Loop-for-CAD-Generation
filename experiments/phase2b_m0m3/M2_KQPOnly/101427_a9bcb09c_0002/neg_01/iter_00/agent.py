import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle 1930 x 550 mm, extrude 50 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Rectangle in UV plane: u from 0 to 1930, v from 0 to 550
# Extrude in +w direction (Y axis) by 50 mm

# Build on XY plane, then rotate to match frame orientation
# Frame: u=X, v=-Z, w=Y
# So rectangle in XZ plane (u=X, v=-Z) -> extrude along Y

# Create rectangle on XZ plane
result = (cq.Workplane("XZ")
          .center(1930/2, 550/2)  # center at midpoint
          .rect(1930, 550)
          .extrude(50.0))

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101427_a9bcb09c_0002\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)