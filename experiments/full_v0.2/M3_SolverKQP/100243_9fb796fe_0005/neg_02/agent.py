import cadquery as cq

# Design Plan: Drone Leg Left - square strut
# Profile: rectangle 19mm x 19mm, extruded 200mm along w direction
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The profile is defined in UV space, with corners at:
#   (-58.2782, -12.0401), (-58.2782, -13.9401), (-56.3782, -13.9401), (-56.3782, -12.0401)
# This gives a rectangle of size 1.9 x 1.9 in UV space, but dimensions say 19.0 x 19.0 mm.
# The UV coordinates appear to be in cm (since compiler note says cm_to_mm x10).
# So we scale by 10 to get mm: rectangle 19mm x 19mm.
# The extrude distance is 200.0 mm.
# We'll build the rectangle centered at origin in the XY plane, then extrude along Z.
# But the frame has w_dir = (0,1,0), so the extrusion direction is Y.
# We'll create the rectangle in the XZ plane and extrude along Y.

# Build the profile: rectangle 19mm x 19mm, centered at origin
# In UV space: u corresponds to X, v corresponds to Z (since v_dir = (0,0,-1), but we can flip)
# Actually v_dir = (0,0,-1) means v axis points in -Z direction.
# To keep it simple, we'll create the rectangle in the XZ plane with positive dimensions.

# The rectangle corners in UV (cm): 
#   (-58.2782, -12.0401) -> (-582.782, -120.401) in mm
#   (-58.2782, -13.9401) -> (-582.782, -139.401) in mm
#   (-56.3782, -13.9401) -> (-563.782, -139.401) in mm
#   (-56.3782, -12.0401) -> (-563.782, -120.401) in mm
# This is a 19mm x 19mm rectangle at a specific location.
# But the design plan says the part is a square strut, likely centered.
# The dimensions say length_u=19, width_v=19, so we'll center it.

# Create the rectangle centered at origin in the XZ plane
profile = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(19.0, 19.0)
)

# Extrude along Y (positive Y direction) by 200 mm
result = profile.extrude(200.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\100243_9fb796fe_0005\\neg_02/generated.step")
