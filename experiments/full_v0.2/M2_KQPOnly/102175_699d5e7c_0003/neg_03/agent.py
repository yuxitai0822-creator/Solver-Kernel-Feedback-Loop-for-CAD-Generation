import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the UV plane, then extruded in the +W direction.
# Note: The design plan uses a coordinate system where the rectangle corners are at:
#   start_uv = (-3.9, 6.8) to (0.0, 6.8) etc.
# This implies the rectangle spans from u=-3.9 to u=0.0 (length 3.9) and v=0.0 to v=6.8 (width 6.8).
# However, the dimensions table says length_u=39.0 and width_v=68.0.
# The compiler note says "unit_conversion_applied: cm_to_mm (x10)".
# So the actual dimensions in mm are: length_u = 3.9 * 10 = 39.0 mm, width_v = 6.8 * 10 = 68.0 mm.
# The extrude distance is 10.0 mm (already in mm).
# We'll create the rectangle centered at the origin for simplicity, then extrude.

# Create the rectangle profile (centered at origin)
result = (cq.Workplane("XY")
          .rect(39.0, 68.0)
          .extrude(10.0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102175_699d5e7c_0003\\neg_03/generated.step")
