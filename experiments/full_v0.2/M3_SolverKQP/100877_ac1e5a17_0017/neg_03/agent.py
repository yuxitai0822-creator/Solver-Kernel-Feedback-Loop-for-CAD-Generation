import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The design plan specifies:
# - Rectangle profile: 254.0 mm x 190.5 mm (note: the curves show 25.4 and 19.05, but dimensions say 254.0 and 190.5)
#   The curves are in UV space and the dimensions are the actual physical sizes.
#   The curves show 25.4 and 19.05 which are 1/10th of the actual dimensions.
#   This is because the design plan notes "unit_conversion_applied: cm_to_mm (x10)"
#   So the actual dimensions are 254.0 mm x 190.5 mm.
# - Extrude distance: 3.175 mm

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\100877_ac1e5a17_0017\\neg_03/generated.step")
