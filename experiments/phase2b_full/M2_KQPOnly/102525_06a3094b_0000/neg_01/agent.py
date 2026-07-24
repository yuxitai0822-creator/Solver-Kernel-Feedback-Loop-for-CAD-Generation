import cadquery as cq

# Design Plan: rectangular prism (SOIC-8 body)
# Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Origin at bbox_min_corner, so we place the rectangle in the uv-plane accordingly.

# The profile rectangle in uv coordinates:
# u from -0.195 to 0.195 (half of 3.9? Actually 3.9/2 = 1.95, but the plan gives 0.195 — likely cm->mm conversion factor 10? 
# The plan states unit_conversion_applied: cm_to_mm (x10). So the uv values in the plan are in cm, we must multiply by 10 to get mm.
# start_uv: [0.19499999999999995, -0.24500000000000005] -> u=1.95, v=-2.45
# end_uv: [0.19499999999999995, 0.245] -> u=1.95, v=2.45
# So rectangle spans u: -1.95 to 1.95, v: -2.45 to 2.45
# That gives length_u = 3.9 mm, width_v = 4.9 mm. Correct.

# Build the rectangle in the uv-plane, then extrude along w (which is y-axis in world).
# Since v_dir = (0,0,-1), the v-axis is negative z. But we can just work in the local frame.
# We'll create a workplane on the xz-plane? Actually easier: create a rectangle in the plane defined by u and v.
# u = x-axis, v = -z axis, w = y axis.
# So the rectangle lies in the xz-plane, with v mapping to -z.
# We'll create a workplane on the front (XZ) plane? Actually cq.Workplane("XZ") gives plane with x and z axes.
# But v_dir = (0,0,-1) means v points along negative z. So we need to flip the z coordinate.
# Simpler: just create the rectangle in the XY plane and then rotate? 
# Let's directly use the local frame: we can create a box centered at origin with dimensions 3.9 x 4.9 x 1.55,
# but the origin convention is bbox_min_corner, so we need to shift so that the box starts at (0,0,0) in local frame.
# Actually the plan says origin_convention: bbox_min_corner. That means the bounding box minimum corner is at (0,0,0) in local coordinates.
# The rectangle uv coordinates are given relative to that origin? The start_uv and end_uv values are in the uv-plane.
# The uv coordinates range from -1.95 to 1.95 in u, and -2.45 to 2.45 in v. So the rectangle is centered at (0,0) in uv-plane.
# But bbox_min_corner means the overall part's bounding box minimum corner is at (0,0,0) in world? 
# Actually the plan says origin_convention: bbox_min_corner, meaning the origin of the local coordinate system is at the minimum corner of the bounding box.
# So the rectangle should be placed such that its min corner is at (0,0) in uv? But the uv values are symmetric around 0.
# This is ambiguous. However, the validation intents expect spans: u_span=3.9, v_span=4.9, w_span=1.55.
# So we just need a box of those dimensions. The position doesn't matter for validation as long as spans are correct.
# We'll create a box centered at origin and then translate so that min corner is at (0,0,0) in world coordinates.
# But the frame axes: u=(1,0,0), v=(0,0,-1), w=(0,1,0). So the box dimensions: along u=3.9, along v=4.9, along w=1.55.
# In world: x spans 3.9, z spans 4.9 (but v is negative z, so we need to handle sign), y spans 1.55.
# To get bbox_min_corner at origin, we can create the box with positive dimensions and then translate.

# Let's create a box from (0,0,0) to (3.9, 1.55, 4.9) but then we need to map v to -z. 
# Actually simpler: create a workplane on the plane defined by u and v, draw rectangle, extrude along w.
# We'll use cq.Workplane("XY") and then rotate? 
# Let's just create a box directly with the correct orientation.

# The local frame: u = x, v = -z, w = y.
# So a point (u, v, w) in local = (x, y, -z) in world? Wait: v = -z, so z = -v. w = y.
# So local (u, v, w) maps to world (x=u, y=w, z=-v).
# The rectangle in uv-plane: u from -1.95 to 1.95, v from -2.45 to 2.45.
# Extrude along w from 0 to 1.55 (one_side, +w direction).
# So in world: x from -1.95 to 1.95, y from 0 to 1.55, z from -2.45 to 2.45 (since z = -v, v from -2.45 to 2.45 gives z from 2.45 to -2.45, i.e., -2.45 to 2.45).
# The bounding box min corner in world is (-1.95, 0, -2.45). To make min corner at (0,0,0), we translate by (1.95, 0, 2.45).

# Let's build step by step.

# Create the rectangle in the uv-plane (which is xz-plane in world, but with v reversed).
# We'll use a workplane on the XZ plane, but note that v = -z, so we need to negate the z coordinate.
# Alternatively, create the rectangle in the XY plane and then rotate? 
# Let's just use the box approach with translation.

# Define dimensions
length_u = 3.9  # along x
width_v = 4.9   # along z (but v = -z, so magnitude is 4.9)
extrude_h = 1.55 # along y

# Create a box centered at origin with dimensions length_u, extrude_h, width_v
# Then translate so that min corner is at (0,0,0)
# The box from (-length_u/2, -extrude_h/2, -width_v/2) to (length_u/2, extrude_h/2, width_v/2)
# Min corner is (-length_u/2, -extrude_h/2, -width_v/2). Translate by (length_u/2, extrude_h/2, width_v/2) to get min at (0,0,0).

result = cq.Workplane("XY").box(length_u, extrude_h, width_v, centered=(True, True, True))
# Translate so that the minimum corner is at (0,0,0)
result = result.translate((length_u/2, extrude_h/2, width_v/2))

# Now we need to ensure the orientation matches the frame: u=x, v=-z, w=y.
# Our box currently has x from 0 to 3.9, y from 0 to 1.55, z from 0 to 4.9.
# But the design expects v span = 4.9 along v direction which is (0,0,-1). So the span along negative z is 4.9, which is correct.
# The w span = 1.55 along y, correct.
# The u span = 3.9 along x, correct.
# So this matches.

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102525_06a3094b_0000\neg_01/generated.step")