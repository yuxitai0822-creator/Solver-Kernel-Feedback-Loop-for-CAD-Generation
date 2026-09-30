import cadquery as cq

# Create a rectangular profile in the XY plane
# The profile dimensions are: length_u = 95.25 mm, width_v = 571.5 mm
# The rectangle is defined by its corner points in UV space:
#   (0, 0), (9.525, 0), (9.525, 57.15), (0, 57.15)
# Note: The UV coordinates in the design plan are scaled by a factor of 10
# (since the compiler notes indicate cm_to_mm conversion x10).
# The actual dimensions are: length_u = 95.25 mm, width_v = 571.5 mm.
# The UV coordinates given are: u from 0 to 9.525, v from 0 to 57.15.
# To get the correct mm dimensions, we multiply by 10:
#   u_span = 9.525 * 10 = 95.25 mm
#   v_span = 57.15 * 10 = 571.5 mm
# So we create a rectangle with those dimensions.

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(95.25, 571.5)
    .extrude(19.05)  # extrude distance = 19.05 mm in +Z direction
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101269_f084ba14_0023\\ex2/generated.step")
