import cadquery as cq
from cadquery import exporters

# Design Plan: Stock - flat rectangular plate
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108412_8de2f9c3_0000\neg_02\iter_01\generated.step"

# Dimensions from design plan (in mm)
length_u = 2438.4  # along x-axis
width_v = 1219.2   # along y-axis
extrude_distance = 12.7  # along z-axis

# Create the rectangular plate centered at origin
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP using correct function name
exporters.export(result, OUT_STEP_PATH)
