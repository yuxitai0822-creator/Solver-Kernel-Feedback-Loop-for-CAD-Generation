import cadquery as cq

# Design Plan: Washer (2)
# Dimensions from plan:
#   outer_radius = 3.49 mm (note: plan shows 0.349 but unit conversion cm->mm x10 applied, so 3.49 mm)
#   inner_radius = 2.0 mm (plan shows 0.2, cm->mm x10 => 2.0 mm)
#   thickness = 0.36 mm (plan shows 0.36, already mm)

# Build washer as extruded annulus
result = (
    cq.Workplane("XY")
    .circle(3.49)  # outer circle
    .circle(2.0)   # inner circle (hole)
    .extrude(0.36) # extrude to thickness
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\107055_0500fdd1_0027\\ex2/generated.step")
