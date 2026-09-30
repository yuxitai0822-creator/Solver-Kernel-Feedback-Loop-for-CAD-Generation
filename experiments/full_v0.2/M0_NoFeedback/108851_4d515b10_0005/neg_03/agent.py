import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle with length_u = 307.848 mm and width_v = 19.05 mm
# Extrude distance = 12.7 mm in the +w direction

# Define the rectangle dimensions
length_u = 307.848  # mm (along x-axis in local frame)
width_v = 19.05     # mm (along z-axis in local frame, since v_dir = [0,0,-1])
extrude_distance = 12.7  # mm (along y-axis in local frame, since w_dir = [0,1,0])

# Create the base rectangle on the XY plane (we'll position it appropriately)
# The design plan uses a local frame where:
#   u_dir = [1,0,0] (x-axis)
#   v_dir = [0,0,-1] (negative z-axis)
#   w_dir = [0,1,0] (y-axis)
# The profile is defined in UV space, and extrude is along +w (y-axis)
# The rectangle corners in UV: (0,0), (30.7848, 0), (30.7848, 1.905), (0, 1.905)
# Note: The UV coordinates are scaled: the actual dimensions are length_u and width_v
# The UV values (30.7848, 1.905) correspond to (307.848, 19.05) after scaling by 10x
# (since compiler notes say cm_to_mm x10 conversion was applied)

# Build the plate: rectangle on XY plane, extruded in Z direction
# Then rotate/translate to match the local frame orientation

# Step 1: Create the rectangle on the XY plane (centered at origin for simplicity)
# The rectangle spans from (0,0) to (length_u, width_v) in UV space
# In the local frame, U is along X, V is along Z (negative direction)
# We'll create the rectangle in the XY plane and then rotate

# Create the base rectangle
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# The resulting box is centered at origin with dimensions:
#   x: -length_u/2 to length_u/2
#   y: -width_v/2 to width_v/2
#   z: 0 to extrude_distance

# We need to reposition so that the origin is at the min corner (bbox_min_corner convention)
# and align with the local frame:
#   u_dir = [1,0,0] (x-axis)
#   v_dir = [0,0,-1] (negative z-axis)
#   w_dir = [0,1,0] (y-axis)
# The extrude is along +w = +y

# To match the design plan, we want:
# - The rectangle in the UV plane (U along X, V along Z) 
# - Extruded along Y (w direction)
# - Origin at the min corner of the bounding box

# The current box has min corner at (-length_u/2, -width_v/2, 0)
# We need to translate so that min corner is at (0,0,0)
# But also need to handle the v_dir = [0,0,-1] which means V axis is negative Z
# This means the rectangle's V dimension goes from 0 to -width_v in Z

# Let's rebuild with proper orientation:
# Create a box with dimensions length_u (x), extrude_distance (y), width_v (z)
# Then position so that the origin is at the min corner

result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
    .translate((length_u/2, extrude_distance/2, -width_v/2))
)

# Now the box spans:
#   x: 0 to length_u
#   y: 0 to extrude_distance
#   z: -width_v to 0
# This matches the local frame where v_dir = [0,0,-1] (V goes negative Z)
# and w_dir = [0,1,0] (W goes positive Y)

# Export the result
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\108851_4d515b10_0005\neg_03/generated.step")
