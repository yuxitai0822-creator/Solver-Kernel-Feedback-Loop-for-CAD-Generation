import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle corners in UV: 
#   start_uv = (121.17356129030935, 31.299551148092803)
#   end_uv = (-0.7464387096940412, 290.379551148076)
# So the rectangle spans from u_min = -0.7464387096940412 to u_max = 121.17356129030935
# and v_min = 31.299551148092803 to v_max = 290.379551148076
# The width in u = 121.17356129030935 - (-0.7464387096940412) = 121.92 (but expected 1219.2? Wait, check: 
#   Actually the design plan says length_u = 1219.2, width_v = 2590.8. 
#   The UV coordinates given are in mm? The plan says unit_conversion_applied: cm_to_mm (x10).
#   The raw UV values: u span = 121.17356129030935 - (-0.7464387096940412) = 121.92 mm? That's 121.92, not 1219.2.
#   But the plan says length_u = 1219.2. Possibly the UV coordinates are in cm? 
#   The plan says unit_conversion_applied: cm_to_mm (x10). So original cm values were multiplied by 10 to get mm.
#   The UV coordinates given are already in mm? Let's check: 121.92 mm = 12.192 cm, but expected 1219.2 mm = 121.92 cm.
#   There's a factor of 10 discrepancy. The plan says "inferred_from_point_span" for dimensions, 
#   and the UV coordinates might be in the original cm? Actually the plan says unit_conversion_applied: cm_to_mm (x10).
#   That means the dimensions in the plan are already in mm (converted from cm). 
#   The UV coordinates might be in the original coordinate system before conversion? 
#   But the plan says coordinate_system unit is mm. 
#   Let's trust the explicit dimensions: length_u = 1219.2, width_v = 2590.8, extrude = 44.45.
#   The UV coordinates given are just for the rectangle corners; the actual size should match the dimensions.
#   The UV span from the coordinates: u_span = 121.17356129030935 - (-0.7464387096940412) = 121.92 mm.
#   But expected u_span = 1219.2 mm. So the UV coordinates are off by factor 10? 
#   Possibly the UV coordinates are in cm? But the plan says unit is mm. 
#   Let's re-examine: The plan says "unit_conversion_applied: cm_to_mm (x10)". 
#   This means the original source was in cm, and all values in the plan have been multiplied by 10 to convert to mm.
#   So the UV coordinates should already be in mm. But 121.92 mm != 1219.2 mm. 
#   Maybe the UV coordinates are not the full span? The rectangle corners are given, but maybe the rectangle is not aligned with the axes? 
#   The frame: u_dir = (1,0,0), v_dir = (0,0,-1). So u is along X, v is along -Z.
#   The rectangle in UV: start_uv = (121.17356129030935, 31.299551148092803), end_uv = (-0.7464387096940412, 290.379551148076).
#   The u coordinates: from -0.746 to 121.174 => span = 121.92. 
#   The v coordinates: from 31.30 to 290.38 => span = 259.08. 
#   But expected width_v = 2590.8. So v_span is also off by factor 10. 
#   So the UV coordinates are in cm? But the plan says unit is mm. 
#   Perhaps the UV coordinates are in the original source units (cm) and the conversion factor was applied to the dimensions only? 
#   The plan says "unit_conversion_applied: cm_to_mm (x10)" and "inferred_dimensions: length_u, width_v". 
#   The dimensions are inferred from point span, so the point span in cm would be 121.92 cm = 1219.2 mm, and 259.08 cm = 2590.8 mm.
#   So the UV coordinates are in cm! The plan's coordinate system says unit mm, but the UV values are in cm before conversion.
#   To be consistent, we should use the dimensions as given: length_u = 1219.2 mm, width_v = 2590.8 mm.
#   The rectangle center can be computed from the UV coordinates (in cm) converted to mm: 
#   u_center_cm = (121.17356129030935 + (-0.7464387096940412)) / 2 = 60.21356129030765 cm = 602.1356129030765 mm
#   v_center_cm = (31.299551148092803 + 290.379551148076) / 2 = 160.8395511480844 cm = 1608.395511480844 mm
#   But we can just create a rectangle centered at origin with the given dimensions, then translate? 
#   The plan doesn't specify absolute position in world coordinates; it's part-local with origin at bbox min corner.
#   The origin_convention is bbox_min_corner, meaning the part's bounding box minimum corner is at (0,0,0) in part-local frame.
#   So we should create a box from (0,0,0) to (1219.2, 44.45, 2590.8) in the frame axes? 
#   Wait: The frame: u_dir = (1,0,0) = X, v_dir = (0,0,-1) = -Z, w_dir = (0,1,0) = Y.
#   So u is X, v is -Z, w is Y.
#   The rectangle is in the UV plane, so it lies in the X-Z plane (with v along -Z).
#   Extrude direction is +w = +Y.
#   So the part is a rectangular block with dimensions: length_u (X) = 1219.2, width_v (Z) = 2590.8, extrude (Y) = 44.45.
#   The origin is at bbox min corner, so the block should be from (0,0,0) to (1219.2, 44.45, 2590.8).
#   But the rectangle UV coordinates suggest the rectangle is not at the origin? 
#   The UV coordinates in cm: u from -0.746 to 121.174, v from 31.30 to 290.38. 
#   In mm: u from -7.464 to 1211.74, v from 313.0 to 2903.8. 
#   But the expected dimensions are 1219.2 x 2590.8. The span in u is 1219.2 mm (121.92 cm), span in v is 2590.8 mm (259.08 cm).
#   The min corner in u is -7.464 mm, min corner in v is 313.0 mm. 
#   If we shift so that min corner is at 0, then the rectangle would be from (0,0) to (1219.2, 2590.8) in UV.
#   But the v coordinate min is 313.0 mm, which is not zero. 
#   The origin convention is bbox_min_corner, so the part's bounding box should have its minimum corner at (0,0,0).
#   Therefore, we should create the rectangle such that its min corner in UV is at (0,0). 
#   The given UV coordinates are just for reference; we can ignore the exact positions and use the dimensions.
#   So: create a rectangle in the X-Z plane (since u=X, v=-Z) with width X = 1219.2, height Z = 2590.8.
#   Then extrude along Y by 44.45.
#   The result will be a box from (0,0,0) to (1219.2, 44.45, 2590.8).

# Build the part
result = (
    cq.Workplane("XY")
    .rect(1219.2, 2590.8)  # rectangle in XY plane, but we need it in XZ? 
    # Actually, rect() creates a rectangle in the current workplane. 
    # Default workplane is XY, so rect(1219.2, 2590.8) creates a rectangle centered at origin with width along X and height along Y.
    # But we want the rectangle in the XZ plane (u=X, v=-Z). 
    # We can work on the XZ plane: cq.Workplane("XZ") gives a plane with X and Z axes.
    # Then rect(1219.2, 2590.8) will create a rectangle in XZ, centered at origin.
    # Then extrude along the normal of XZ plane, which is Y. But we need extrude along +Y (which is +w).
    # The normal of XZ plane is Y, but direction? XZ plane normal is (0,1,0) = +Y. So extrude will go in +Y.
    # However, we need the rectangle to be positioned such that its min corner is at origin.
    # rect() creates centered rectangle. We can use .center() to shift or use .box() directly.
    # Simpler: use cq.Workplane("XY").box(1219.2, 44.45, 2590.8) but that would create a box centered at origin.
    # We need the box from (0,0,0) to (1219.2, 44.45, 2590.8). 
    # So we can create a box and then translate it by half dimensions.
    # Or use .box() with centered=False? cq's box() always centers. 
    # We can use .add() with a solid box at the desired position.
)

# Alternative: create a box from (0,0,0) to (1219.2, 44.45, 2590.8)
# Using cq.Workplane("XY").box(1219.2, 44.45, 2590.8).translate((1219.2/2, 44.45/2, 2590.8/2))
# But that would center at origin then translate to positive quadrant.
# Actually, box() creates a box centered at origin. To get min corner at origin, translate by half dimensions.

result = cq.Workplane("XY").box(1219.2, 44.45, 2590.8).translate((1219.2/2, 44.45/2, 2590.8/2))

# But wait: the frame has v_dir = (0,0,-1), meaning v is along -Z. 
# In our box, the Z dimension is 2590.8, but the v direction is -Z. 
# That means the rectangle's v coordinate increases in the -Z direction. 
# If we want the min corner at origin, and v increases along -Z, then the box should extend in the -Z direction from origin.
# But the bbox min corner convention means the minimum corner of the bounding box is at origin.
# If v increases along -Z, then the minimum v (most negative) would be at the origin? 
# Actually, if v_dir = (0,0,-1), then v coordinate is measured along -Z. 
# So a point with v=0 is at Z=0, and a point with v=2590.8 is at Z=-2590.8.
# The bounding box min corner in world coordinates would be at (0,0,-2590.8) if we place the rectangle from v=0 to v=2590.8.
# But the origin convention is bbox_min_corner, meaning the part's bounding box minimum corner is at (0,0,0) in part-local frame.
# So we need to shift so that the minimum corner (which is at Z=-2590.8) becomes 0.
# That means we need to translate the box by (0,0,2590.8) so that the min Z is at 0.
# But then the rectangle's v coordinate would go from 0 to 2590.8 in the -Z direction? 
# Let's think: If we have a box from (0,0,0) to (1219.2, 44.45, 2590.8) in XYZ, then the v coordinate (along -Z) 
# at Z=0 is v=0, at Z=2590.8 is v=-2590.8. So v spans from 0 to -2590.8, which is a span of 2590.8 but negative direction.
# The design plan says width_v = 2590.8 (positive), so the span magnitude is correct.
# The min corner in world coordinates would be at (0,0,0) (since we placed it there). 
# But the v coordinate at that corner is v=0 (since Z=0). The max v is at Z=2590.8, v=-2590.8. 
# So the v span is from -2590.8 to 0, which is a span of 2590.8. That's fine.
# The origin convention says bbox_min_corner, so the minimum corner of the bounding box is at (0,0,0). 
# In our box, the minimum corner is at (0,0,0) (since all coordinates are non-negative). 
# So this is correct.

# But we need to ensure the rectangle is in the UV plane. The UV plane is defined by u_dir and v_dir.
# u_dir = (1,0,0) = X, v_dir = (0,0,-1) = -Z. So the UV plane is the X-Z plane, but with v reversed.
# Our box has its rectangle face in the X-Z plane (the face at Y=0 and Y=44.45). 
# The rectangle is extruded along +w = +Y. So the extrusion direction is Y.
# Our box is extruded along Y from 0 to 44.45. That matches.

# So the final result is a box from (0,0,0) to (1219.2, 44.45, 2590.8).

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\108244_329b1876_0000\neg_03/generated.step")