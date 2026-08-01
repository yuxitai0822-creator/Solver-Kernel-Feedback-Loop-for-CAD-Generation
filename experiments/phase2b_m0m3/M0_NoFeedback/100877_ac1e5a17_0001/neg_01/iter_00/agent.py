import cadquery as cq
from cadquery import exporters

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm (extrude distance)
# The perturbed value from previous iteration (2.38125 mm) is replaced with the correct 1.5875 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100877_ac1e5a17_0001\neg_01\iter_00/generated.step"

# Create the rectangular profile on XY plane
# Rectangle centered at origin with dimensions 279.4 x 215.9 mm
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)  # extrude distance in mm
)

# Export to STEP file
exporters.export(result, OUT_STEP_PATH)
