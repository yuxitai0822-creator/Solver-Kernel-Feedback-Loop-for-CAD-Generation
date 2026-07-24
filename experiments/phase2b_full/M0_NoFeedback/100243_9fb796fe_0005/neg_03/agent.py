import cadquery as cq

# Create a rectangular profile in the UV plane
# The profile is a 19mm x 19mm square centered at the origin
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# The profile coordinates in UV space are:
#   u range: [-58.27820137826746, -56.37820137826746]  -> width = 1.9 (but expected 19mm)
#   v range: [-13.940145769681571, -12.04014576968157] -> height = 1.9 (but expected 19mm)
# Note: The design plan says dimensions are 19mm x 19mm, but the UV coordinates
# span only 1.9 units. This is likely because the source was in cm and converted to mm (x10).
# The UV coordinates appear to be in cm, so we multiply by 10 to get mm.
# Actually, the compiler notes say "unit_conversion_applied: cm_to_mm (x10)",
# meaning the dimensions in the plan are already in mm. The UV coordinates
# are given as-is from the source, which was in cm. So we need to scale them by 10.

# Let's compute the center and size in UV space (original cm values):
# u_center = (-58.27820137826746 + -56.37820137826746) / 2 = -57.32820137826746
# v_center = (-13.940145769681571 + -12.04014576968157) / 2 = -12.99014576968157
# u_size = 1.9 cm = 19 mm
# v_size = 1.9 cm = 19 mm

# So we create a 19mm x 19mm square centered at (-57.3282, -12.9901) in UV space
# But since we're working in mm, we can just create the rectangle at the origin
# and then translate it. However, the frame orientation matters.

# The frame has:
#   u_dir = [1, 0, 0]  (X axis)
#   v_dir = [0, 0, -1] (negative Z axis)
#   w_dir = [0, 1, 0]  (Y axis)
# So the profile lies in the X-Z plane (u=X, v=-Z), and extrudes along Y (w=Y)

# Create the rectangle in the XZ plane
# The rectangle is 19mm x 19mm, centered at the origin in UV space
# But the plan specifies the rectangle at a specific location in UV space.
# We'll create it at the correct UV position.

# Convert UV center to XYZ:
#   X = u = -57.32820137826746
#   Z = -v = 12.99014576968157  (since v_dir = [0,0,-1], so Z = -v)
#   Y = 0 (profile is at w=0)

# Create the rectangle
result = (cq.Workplane("XZ")
    .center(-57.32820137826746, 12.99014576968157)
    .rect(19.0, 19.0)
    .extrude(200.0))

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\100243_9fb796fe_0005\neg_03/generated.step")
