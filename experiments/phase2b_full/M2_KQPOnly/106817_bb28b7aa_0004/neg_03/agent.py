import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions (in mm):
#   Outer radius = 5.5372 mm
#   Inner radius = 1.9812 mm
#   Thickness (extrude distance) = 1.3208 mm
#   Center in UV plane: (-25.400001, 12.7) but we place at origin for simplicity

# Build the washer by creating a circle for outer and inner, then extrude
result = (
    cq.Workplane("XY")
    .circle(5.5372)          # outer circle
    .circle(1.9812)          # inner circle (hole)
    .extrude(1.3208)         # extrude to thickness
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106817_bb28b7aa_0004\\neg_03/generated.step")
