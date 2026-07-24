import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the uv-plane, then extruded in the +w direction.
# Note: The design plan uses a coordinate system where the rectangle corners are at:
#   start_uv = (-3.9, 6.8) to (0.0, 6.8) etc.
# This describes a rectangle of width 3.9 (in u) and height 6.8 (in v).
# However, the dimensions section says length_u = 39.0 and width_v = 68.0.
# The compiler note says unit_conversion_applied: cm_to_mm (x10).
# So the uv coordinates in the profile are in cm (3.9 cm = 39 mm, 6.8 cm = 68 mm).
# We will build the rectangle directly in mm using the explicit dimensions.

# Build the rectangle profile centered at origin for simplicity, then extrude.
result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102175_699d5e7c_0003\ex2/generated.step")
