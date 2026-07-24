import cadquery as cq

# Create a rectangular profile based on the design plan
# The profile is defined in UV space where:
# - U direction corresponds to X axis (length_u = 95.25 mm)
# - V direction corresponds to Z axis (width_v = 571.5 mm)
# The rectangle corners are given in UV coordinates:
#   (0,0), (9.525,0), (9.525,57.15), (0,57.15)
# Note: The UV coordinates appear to be scaled by 10 relative to the actual dimensions.
# The actual dimensions are length_u=95.25 and width_v=571.5.
# The UV coordinates in the plan are 9.525 and 57.15, which are exactly 1/10 of the actual.
# This suggests the source was in cm and converted to mm by multiplying by 10.
# So we use the actual dimensions directly.

length_u = 95.25  # mm
width_v = 571.5   # mm
extrude_distance = 19.05  # mm

# Create the rectangle in the XY plane (U=X, V=Y)
# The profile will be extruded in the +Z direction (W direction)
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101269_f084ba14_0023\\neg_01/generated.step")
