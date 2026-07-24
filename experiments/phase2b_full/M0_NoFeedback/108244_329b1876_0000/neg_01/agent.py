import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The frame defines u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle in UV space: u from -0.7464 to 121.1736, v from 31.2996 to 290.3796
# But the inferred dimensions are 1219.2 x 2590.8, so the UV coordinates are scaled by 10 (cm->mm conversion).
# We'll build the rectangle centered at origin for simplicity, then translate to match the UV origin.

# Create the rectangle profile in the XY plane (since u_dir = X, v_dir = Z negative, w_dir = Y)
# We'll work in the standard XY plane and then rotate/translate as needed.
# Actually, the frame: u_dir = X, v_dir = -Z, w_dir = Y. So the profile lies in the X-Z plane (u-v plane).
# Extrude direction is +w = +Y.

# Let's build a workplane on the XZ plane (front view) and draw the rectangle.
# The rectangle spans: u from -0.7464 to 121.1736 (scaled by 10? Actually the values are in mm already? 
# The design plan says unit_conversion_applied: cm_to_mm (x10). So the UV values are in cm? 
# The inferred dimensions are 1219.2 mm and 2590.8 mm. The UV span: (121.1736 - (-0.7464)) = 121.92 cm = 1219.2 mm. 
# Similarly v span: (290.3796 - 31.2996) = 259.08 cm = 2590.8 mm. So UV coordinates are in cm, but we need mm.
# So we multiply by 10 to get mm.

# Build the rectangle in the XZ plane (u = X, v = Z).
# The rectangle corners in mm:
# u_min = -0.7464387096940412 * 10 = -7.464387096940412 mm
# u_max = 121.17356129030935 * 10 = 1211.7356129030935 mm
# v_min = 31.299551148092803 * 10 = 312.99551148092803 mm
# v_max = 290.379551148076 * 10 = 2903.79551148076 mm

# But the inferred dimensions are 1219.2 x 2590.8, which matches the span: (1211.7356 - (-7.4644)) = 1219.2, (2903.7955 - 312.9955) = 2590.8.

# We'll create the rectangle centered at the origin for simplicity, then translate.
# Actually, let's just create the rectangle at the correct position.

# Workplane on XZ plane (front view). In CadQuery, the default workplane is XY. 
# To work in XZ, we can use workplane("XZ") or workplane(offset=0, direction=(0,1,0)).
# Let's use workplane("XZ") which gives us a plane with normal Y.

# The rectangle in UV: u along X, v along Z.
# We'll create a rectangle from corner to corner.

# Define the rectangle corners in mm (scaled by 10 from UV):
u_min = -0.7464387096940412 * 10
u_max = 121.17356129030935 * 10
v_min = 31.299551148092803 * 10
v_max = 290.379551148076 * 10

# Create the rectangle on the XZ plane
result = (cq.Workplane("XZ")
          .rect(u_max - u_min, v_max - v_min, centered=False)
          .extrude(44.45)  # extrude along Y (positive w direction)
         )

# The rect() with centered=False places the first corner at (0,0) in the workplane coordinates.
# We need to translate so that the rectangle spans from u_min to u_max in X and v_min to v_max in Z.
# The rect() with centered=False: the first corner is at (0,0) and the rectangle extends to (width, height).
# So we need to translate by (u_min, v_min) in the workplane coordinates.
# But note: workplane("XZ") has X as first axis, Z as second axis.
# So we translate by (u_min, v_min) in the workplane's local coordinates.

# However, the rect() with centered=False places the lower-left corner at (0,0) and the upper-right at (width, height).
# So we need to move the rectangle so that its lower-left corner is at (u_min, v_min).
# That means translating by (u_min, v_min).

result = result.translate((u_min, 0, v_min))

# But wait: the extrude direction is +w = +Y. The workplane is XZ, so extrude goes along Y (normal to XZ).
# The extrude distance is 44.45 mm. That matches the design.

# However, the design plan says the extrude direction is +w, and w_dir = (0,1,0). So extrude along Y positive.
# Our extrude goes along Y positive by default when using workplane("XZ").

# Let's verify the dimensions:
# The resulting solid should have bounding box:
# X: from u_min to u_max (span 1219.2 mm)
# Z: from v_min to v_max (span 2590.8 mm)
# Y: from 0 to 44.45 mm (since we extruded from the XZ plane at Y=0)

# But the design plan's frame origin is at bbox_min_corner. The rectangle's UV coordinates are relative to that origin.
# Our translation places the rectangle correctly in world coordinates.

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108244_329b1876_0000\\neg_01/generated.step")
