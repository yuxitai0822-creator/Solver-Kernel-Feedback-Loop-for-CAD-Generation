import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u = 1930.0 mm, width_v = 550.0 mm, extrude_distance = 50.0 mm
# The design plan specifies a rectangle in UV space with curves at (0,55) -> (0,0) -> (193,0) -> (193,55) -> (0,55)
# With unit_conversion_applied: cm_to_mm (x10), these become 1930 mm x 550 mm
# The perturbation description (original=55.0, perturbed=44.0) is a placeholder and not yet wired
# We follow the design plan exactly as specified

result = (
    cq.Workplane("XY")
    .rect(1930.0, 550.0, centered=True)
    .extrude(50.0)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0002\neg_03\iter_02/generated.step"
exporters.export(result, OUT_STEP_PATH)