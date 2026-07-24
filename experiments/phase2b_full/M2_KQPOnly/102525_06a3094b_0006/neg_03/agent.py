import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is centered on the origin in the XY plane, extruded in +Z direction.

# Create the rectangle profile centered at origin
# Length along u (x-axis) = 11.3 mm, width along v (y-axis) = 21.0 mm
# The profile coordinates from the plan: u from -0.565 to 0.565, v from -1.05 to 1.05
# But those are normalized? Actually the plan says length_u=11.3, width_v=21.0
# The uv coordinates given are half-extents: 0.565 = 11.3/20? No, 11.3/2 = 5.65, not 0.565
# Wait: the plan says unit_conversion_applied: cm_to_mm (x10). So original was in cm, converted to mm.
# The uv coordinates: 0.565 * 10 = 5.65 mm half-length, 1.05 * 10 = 10.5 mm half-width
# So half-length = 5.65 mm, half-width = 10.5 mm => full length = 11.3 mm, full width = 21.0 mm. Correct.

# Build the rectangle centered at origin
result = (cq.Workplane("XY")
          .center(0, 0)
          .rect(11.3, 21.0)
          .extrude(3.0))

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102525_06a3094b_0006\neg_03/generated.step")
