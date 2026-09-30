import cadquery as cq

# Create a rectangular profile based on the design plan
# The profile is a 19mm x 19mm square, centered at the origin in the UV plane
# The rectangle corners are given in UV coordinates:
#   (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
# This is a 2mm x 1.9mm rectangle? Wait, let's check dimensions:
#   U span: -56.37820137826746 - (-58.27820137826746) = 1.9 mm? No, that's 1.9? Actually 58.2782 - 56.3782 = 1.9
#   V span: -12.04014576968157 - (-13.940145769681571) = 1.9 mm
# But the design plan says length_u = 19.0, width_v = 19.0. There's a factor of 10 discrepancy.
# The compiler notes say "unit_conversion_applied: cm_to_mm (x10)". So the UV coordinates are in cm?
# Actually, the coordinates are likely in the original units (cm) and we need to scale by 10 to get mm.
# Let's scale the coordinates by 10 to get mm.

scale = 10.0

# Original UV coordinates (in cm, from design plan)
u1 = -58.27820137826746
v1 = -12.04014576968157
u2 = -56.37820137826746
v2 = -13.940145769681571

# Scale to mm
u1_mm = u1 * scale
v1_mm = v1 * scale
u2_mm = u2 * scale
v2_mm = v2 * scale

# The rectangle in UV plane (U is along x, V is along z? Actually frame says u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0])
# So U -> X, V -> -Z, W -> Y
# We'll create the rectangle in the XY plane (since CadQuery's default is XY), then transform.
# Actually, let's just create a rectangle centered at origin with correct dimensions.
# The rectangle dimensions: length_u = 19.0 mm, width_v = 19.0 mm
# But the UV coordinates give a 1.9 x 1.9 cm rectangle = 19 x 19 mm. So scaling works.

# Let's compute center and size
center_u = (u1_mm + u2_mm) / 2.0
center_v = (v1_mm + v2_mm) / 2.0
size_u = abs(u2_mm - u1_mm)  # should be 19.0
size_v = abs(v2_mm - v1_mm)  # should be 19.0

# Create the rectangle in the UV plane, then extrude along W (Y axis)
# Since u_dir = X, v_dir = -Z, w_dir = Y
# We'll create the rectangle in the XZ plane (since V is along -Z, we need to handle sign)
# Actually, let's just create a rectangle in the XY plane and then rotate/translate as needed.
# Simpler: create a box directly with the correct dimensions and position.

# The frame says: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the rectangle lies in the plane spanned by X and -Z, extruded along Y.
# In CadQuery, we can create a rectangle on the XZ plane (which is Y=0 plane) and extrude along Y.

# Create the rectangle on the XZ plane (Y=0)
# The rectangle center in UV coordinates is (center_u, center_v).
# In world coordinates: X = center_u, Z = -center_v (since v_dir = -Z), Y = 0
center_x = center_u
center_z = -center_v
center_y = 0.0

# Create the rectangle
rect = cq.Workplane("XZ").center(center_x, center_z).rect(size_u, size_v).extrude(130.0)

# The extrusion direction is along W = Y axis, which is the default for extrude from XZ plane.
# But we need to ensure the extrusion goes in the +Y direction (since extent_type is "one_side", direction "+w").
# The extrude distance is 130.0 mm.

result = rect

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\100243_9fb796fe_0006\\neg_02/generated.step")
