import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions (in mm):
#   outer radius = 5.5372 mm
#   inner radius = 1.9812 mm
#   thickness (extrude distance) = 1.3208 mm
# Center in UV plane: (-25.400001, 12.7) but we place at origin for simplicity.

# Create the outer circle (radius 5.5372)
outer_circle = cq.Workplane("XY").circle(5.5372)

# Create the inner circle (radius 1.9812) as a hole
inner_circle = cq.Workplane("XY").circle(1.9812)

# Build the washer: start with outer circle, cut inner circle, extrude
result = (
    cq.Workplane("XY")
    .circle(5.5372)          # outer boundary
    .circle(1.9812)          # inner boundary (hole)
    .extrude(1.3208)         # extrude along Z by thickness
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106817_bb28b7aa_0004\\neg_02/generated.step")
