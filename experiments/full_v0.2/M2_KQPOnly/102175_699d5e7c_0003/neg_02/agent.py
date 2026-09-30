import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the uv-plane, then extruded in the +w direction.
# Note: The design plan uses a local frame with u_dir=(1,0,0), v_dir=(0,1,0), w_dir=(0,0,1).
# The rectangle corners in uv coordinates are: (-3.9, 0) to (0, 6.8) but the dimensions indicate
# length_u=39.0 and width_v=68.0. The uv coordinates appear to be in cm (since unit_conversion_applied: cm_to_mm x10).
# Converting: -3.9 cm = -39 mm, 0 cm = 0 mm, 6.8 cm = 68 mm.
# So the rectangle spans from u=-39 to u=0 (length 39) and v=0 to v=68 (width 68).
# We'll create the rectangle centered or at origin for simplicity, matching the span.

result = (cq.Workplane("XY")
          .rect(39.0, 68.0, centered=False)
          .extrude(10.0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102175_699d5e7c_0003\\neg_02/generated.step")