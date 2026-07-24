import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the UV plane, then extruded in the +W direction.
# Note: The design plan uses a coordinate system where the rectangle corners are at:
#   start_uv = (-3.9, 6.8) to (0.0, 6.8) etc.
# This describes a rectangle of width 3.9 in U and height 6.8 in V.
# However, the dimensions section says length_u=39.0 and width_v=68.0.
# The compiler notes indicate a unit conversion from cm to mm (x10).
# The UV coordinates in the profile are in cm (3.9 cm = 39 mm, 6.8 cm = 68 mm).
# So we build the rectangle with dimensions 39.0 x 68.0 mm, centered at the origin.
# The extrude distance is 10.0 mm.

# Build the rectangle profile on the XY plane (U=X, V=Y, W=Z)
result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0, centered=True)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102175_699d5e7c_0003\\neg_03/generated.step")
