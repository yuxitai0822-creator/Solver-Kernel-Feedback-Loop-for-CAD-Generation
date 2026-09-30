import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle corners in UV: 
#   start_uv = (121.17356129030935, 31.299551148092803)
#   end_uv = (-0.7464387096940412, 290.379551148076)
# We'll create a rectangle from min to max UV, then extrude.

# Extract UV bounds
uv_points = [
    (121.17356129030935, 31.299551148092803),
    (-0.7464387096940412, 31.299551148092803),
    (121.17356129030935, 290.379551148076),
    (-0.7464387096940412, 290.379551148076)
]

min_u = min(p[0] for p in uv_points)
max_u = max(p[0] for p in uv_points)
min_v = min(p[1] for p in uv_points)
max_v = max(p[1] for p in uv_points)

# Width and height in UV
width_u = max_u - min_u  # should be ~121.92? Actually from dimensions: length_u=1219.2, but UV coords are scaled?
height_v = max_v - min_v  # should be ~259.08? Actually from dimensions: width_v=2590.8

# The design plan says dimensions: length_u=1219.2, width_v=2590.8, extrude=44.45
# The UV coordinates given are not directly the dimensions; they are in some local frame.
# We'll use the explicit dimensions from the plan.

length_u = 1219.2  # mm
width_v = 2590.8   # mm
extrude_distance = 44.45  # mm

# Create rectangle centered at origin in XY plane, then transform to match frame.
# Frame: u_dir = X axis, v_dir = -Z axis, w_dir = Y axis
# So we want: rectangle in XZ plane? Actually v_dir = (0,0,-1) means v is along -Z.
# w_dir = (0,1,0) means extrusion along Y.
# So the profile lies in the X-Z plane (u along X, v along -Z).
# We'll create a rectangle in the XY plane (default) and then rotate.

# Approach: create a box directly with the correct dimensions and orientation.
# Box centered at origin, dimensions: length_u along X, extrude_distance along Y, width_v along Z.
# But careful: v_dir = (0,0,-1) means v is along -Z, so width_v is along Z but negative direction.
# We'll just create a box with positive dimensions and it will be symmetric.

result = cq.Workplane("XY").box(length_u, extrude_distance, width_v, centered=(True, True, True))

# The box is centered at origin. The design plan's origin is at bbox_min_corner.
# We need to shift so that the min corner is at origin.
# The box spans from -length_u/2 to +length_u/2 in X, etc.
# To match bbox_min_corner convention, we translate so that min corner is at (0,0,0).
result = result.translate((length_u/2, extrude_distance/2, width_v/2))

# Now the box occupies: X: 0..length_u, Y: 0..extrude_distance, Z: 0..width_v
# But the frame says v_dir = (0,0,-1), so v coordinate decreases along Z.
# The design plan's UV coordinates have v ranging from ~31 to ~290, which is positive.
# Our Z goes from 0 to width_v, which is 2590.8. That's fine.

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108244_329b1876_0000\\neg_03/generated.step")
