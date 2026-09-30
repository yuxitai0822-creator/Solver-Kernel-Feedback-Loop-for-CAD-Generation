import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the uv-plane, then extruded in the +w direction.
# Note: The design plan uses a coordinate system where the rectangle corners are at:
#   start_uv = (-3.9, 6.8) to (0.0, 6.8) etc.
# This describes a rectangle of width 3.9 (in u) and height 6.8 (in v).
# However, the dimensions section says length_u=39.0 and width_v=68.0.
# The compiler note says unit_conversion_applied: cm_to_mm (x10).
# So the profile coordinates are in cm and need to be multiplied by 10 to get mm.
# 3.9 cm = 39 mm, 6.8 cm = 68 mm. So the rectangle spans from u=-39 to u=0 and v=0 to v=68.
# We'll create the rectangle centered at the origin for simplicity, then translate if needed.
# The extrusion direction is +w, distance 10.0 mm.

# Create the rectangle profile (centered at origin for easier handling)
# Width = 39 mm, Height = 68 mm
result = (cq.Workplane("XY")
          .rect(39.0, 68.0, centered=True)
          .extrude(10.0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102175_699d5e7c_0003\\ex2/generated.step")
