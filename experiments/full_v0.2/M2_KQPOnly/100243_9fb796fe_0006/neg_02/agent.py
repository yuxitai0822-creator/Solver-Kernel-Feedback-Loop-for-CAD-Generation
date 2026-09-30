import cadquery as cq

# Design Plan: Drone Leg - square strut
# Profile: rectangle 19mm x 19mm, extruded 130mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle is defined in UV space with corners at:
#   (-58.2782, -12.0401), (-58.2782, -13.9401), (-56.3782, -13.9401), (-56.3782, -12.0401)
# This gives a rectangle of width = 1.9 (in U) and height = 1.9 (in V).
# But the dimensions say length_u = 19.0, width_v = 19.0.
# The UV coordinates are scaled by 10 (cm to mm conversion).
# So the rectangle in mm is 19mm x 19mm.
# The extrude direction is +w (0,1,0) for 130mm.

# Build the rectangle profile in the UV plane (XZ plane in world?)
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# So UV plane is XZ plane (u=X, v=-Z).
# The rectangle center in UV: u_center = (-58.2782 + -56.3782)/2 = -57.3282
# v_center = (-12.0401 + -13.9401)/2 = -12.9901
# Width in U = 1.9, Width in V = 1.9
# But the dimensions say 19mm, so the UV coords are in mm already (after cm->mm conversion).
# Actually the UV values are -58.2782 etc, which are large offsets. The rectangle size is 1.9.
# But the dimensions say 19.0. There's a factor of 10 discrepancy.
# The compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
# So the UV coordinates are in cm? No, they are in mm after conversion.
# Let's check: difference in U: -56.3782 - (-58.2782) = 1.9. That's 1.9mm, not 19mm.
# But the dimensions say 19.0mm. So the UV coordinates are in cm? 
# Actually the conversion was applied to the original design, so the UV values should be in mm.
# 1.9 cm = 19 mm. So the UV values are in cm? No, they are in mm after conversion.
# Wait: 1.9 (in UV) * 10 = 19mm. So the UV coordinates are in the original cm units.
# The conversion multiplies by 10, so the rectangle in mm is 19mm x 19mm.
# So we need to scale the UV coordinates by 10 to get mm.
# But the extrude distance is 130.0 (already in mm).

# Let's just build a 19mm x 19mm rectangle centered at origin, then extrude 130mm in Y direction.
# The frame says u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0).
# So the profile is in the XZ plane, extruded along Y.

# Create the rectangle profile
result = (cq.Workplane("XZ")
          .rect(19.0, 19.0, centered=True)
          .extrude(130.0))

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100243_9fb796fe_0006\\neg_02/generated.step")
