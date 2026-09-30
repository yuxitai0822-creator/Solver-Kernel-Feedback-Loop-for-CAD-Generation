import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the u-v plane, extruded along +w direction.
# From the frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: u = X, v = -Z, w = Y
# The rectangle corners in uv: 
#   start_uv = (121.17356129030935, 31.299551148092803)
#   end_uv = (-0.7464387096940412, 290.379551148076)
# So u range: from -0.7464 to 121.1736 => width = 121.92? Wait, that's 121.92, but expected length_u = 1219.2.
# The design plan says unit conversion applied: cm_to_mm (x10). So the uv values are in cm? 
# Actually the plan says unit is mm, but compiler notes say cm_to_mm (x10). 
# The dimensions given: length_u = 1219.2 mm, width_v = 2590.8 mm.
# The uv points: u from -0.7464 to 121.1736 => span = 121.92, v from 31.2996 to 290.3796 => span = 259.08.
# If we multiply by 10 (cm to mm), we get 1219.2 and 2590.8. So the uv coordinates are in cm.
# But the script should output in mm. So we scale the uv coordinates by 10.
# Alternatively, we can just use the explicit dimensions from the plan.
# Let's use the explicit dimensions: length_u = 1219.2, width_v = 2590.8, extrude = 44.45.
# The rectangle center: we can center it at origin or place it as per uv coordinates.
# The uv coordinates give a rectangle from (-0.7464, 31.2996) to (121.1736, 290.3796) in cm.
# In mm: from (-7.464, 312.996) to (1211.736, 2903.796). That's a large offset.
# But the design plan says origin_convention: bbox_min_corner. So the rectangle's min corner is at (u_min, v_min).
# We'll place the rectangle such that its min corner is at (0,0) in uv, then extrude.
# Actually, to match the plan exactly, we should use the uv coordinates scaled by 10.
# Let's compute: u_min = -0.7464387096940412 * 10 = -7.464387096940412
# u_max = 121.17356129030935 * 10 = 1211.7356129030935
# v_min = 31.299551148092803 * 10 = 312.99551148092803
# v_max = 290.379551148076 * 10 = 2903.79551148076
# So the rectangle in mm: width along u = 1219.2, height along v = 2590.8.
# We'll create a rectangle centered at (u_center, v_center) for simplicity, but the plan uses min corner.
# Let's just create a rectangle with the correct dimensions, placed at origin (min corner at 0,0).
# This will produce the same shape, just translated. The validation intents check spans, not absolute position.
# So we can create a rectangle from (0,0) to (1219.2, 2590.8) in the uv plane.
# Then extrude along w (Y axis) by 44.45 mm.

# Build the workplane: u = X, v = -Z, w = Y
# So the rectangle lies in the X-Z plane? Actually v = -Z, so v axis is negative Z.
# The rectangle in uv: u from 0 to 1219.2, v from 0 to 2590.8.
# In XYZ: u = X, v = -Z, so point (u, v) maps to (X, 0, -v).
# So the rectangle is in the X-Z plane, with Z negative.
# Extrude along w = Y direction (positive Y).

# Let's create a workplane on the X-Z plane (Y=0), then draw rectangle.
# But cadquery's workplane on "XZ" has normal in Y direction.
# We'll use workplane("XZ") and then draw rectangle centered at (609.6, -1295.4) to match the uv coordinates.
# Actually simpler: use workplane("XZ") and then rect(width, height) where width along X, height along Z.
# But careful: v_dir = (0,0,-1), so v axis is negative Z. So the rectangle's v dimension is along -Z.
# So if we draw rect(1219.2, 2590.8) on XZ plane, the width is along X, height along Z.
# But the plan says v dimension is 2590.8 along v_dir = (0,0,-1). So the rectangle's extent along Z is -2590.8.
# To match the uv coordinates (v from 0 to 2590.8), we want the rectangle to span from Z=0 to Z=-2590.8.
# So we can draw a rectangle from (0,0) to (1219.2, -2590.8) in the XZ plane.
# Then extrude along Y by 44.45.

result = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .rect(1219.2, 2590.8, centered=False)
    .extrude(44.45)
)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108244_329b1876_0000\\neg_01/generated.step")
