import cadquery as cq

# Design Plan: rectangular prism with dimensions 101.6 x 101.6 x 38.1 mm
# The profile is a square centered at origin, with half-side = 5.08 (since start_uv = +/-5.079999...)
# Extrude in +w direction by 38.1 mm

# Create the rectangular profile centered at origin
# The profile vertices from the plan: (5.08, -5.08), (5.08, 5.08), (-5.08, 5.08), (-5.08, -5.08)
# This is a square of side 10.16 mm, but the actual dimensions are 101.6 mm.
# The start_uv values appear to be in cm (since compiler notes say cm_to_mm x10).
# So the actual half-side in mm is 5.08 * 10 = 50.8 mm, giving full side 101.6 mm.
# We'll build directly with the correct mm dimensions.

# Build the profile as a rectangle centered at origin
result = (cq.Workplane("XY")
          .rect(101.6, 101.6, centered=True)
          .extrude(38.1))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\103481_b27a1cdf_0010\\ex2/generated.step")
