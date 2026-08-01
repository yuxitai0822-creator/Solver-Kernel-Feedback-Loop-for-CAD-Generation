import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102410_f9877a7b_0012\neg_02\iter_00\generated.step"

# Design parameters from the design plan (converted to mm)
outer_radius = 6.0  # mm (original 0.6 cm * 10 = 6.0 mm)
inner_radius = 4.25  # mm (original 0.425 cm * 10 = 4.25 mm)
extrude_height = 12.0  # mm (original 1.2 cm * 10 = 12.0 mm)

# Build the annulus (washer shape) using cadquery
# Workplane in XY plane, center at origin
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_height)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
