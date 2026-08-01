import cadquery as cq
from cadquery import exporters

# Design Plan: flat plate, extruded rectangle
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The rectangle is centered at origin in the XY plane, extruded in +Z direction

# Create the rectangle profile centered at origin
result = (
    cq.Workplane("XY")
    .rect(2438.4, 1219.2, centered=True)
    .extrude(12.7)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108412_8de2f9c3_0000\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)