import cadquery as cq

# Design Plan: rectangular prism with dimensions 8.5mm x 18.0mm x 2.5mm
# The profile is a rectangle centered at origin in the XY plane, extruded in +Z direction.
# From the design plan:
#   - u_dir = [1,0,0] (X axis)
#   - v_dir = [0,0,-1] (negative Z axis) but we interpret as width along Y? 
#   - w_dir = [0,1,0] (Y axis) but extrusion direction is +w => along Y?
# Actually the frame has u_dir = X, v_dir = -Z, w_dir = Y.
# The rectangle is defined in UV space: u from -0.425 to 0.425, v from -0.9 to 0.9.
# But the dimensions say length_u = 8.5, width_v = 18.0. 
# The UV coordinates are half-extents: 0.425*2 = 0.85? That doesn't match 8.5.
# Wait: the design plan says unit_conversion_applied: cm_to_mm (x10).
# So the UV values are in cm? 0.425 cm = 4.25 mm, times 2 = 8.5 mm. Yes!
# Similarly 0.9 cm = 9.0 mm, times 2 = 18.0 mm. Perfect.
# So the rectangle in UV space has half-extents (4.25, 9.0) in mm.
# The frame: u_dir = X, v_dir = -Z, w_dir = Y.
# So in 3D: u maps to X, v maps to -Z, w maps to Y.
# The rectangle lies in the X-Z plane (since v is -Z), and extrudes along Y (w direction).
# But typical CAD: we want a flat rectangle on XY plane extruded in Z.
# Let's re-interpret: The design plan says the part is a rectangular prism.
# The dimensions: 8.5 (length_u), 18.0 (width_v), 2.5 (extrude along w).
# The frame: u_dir = X, v_dir = -Z, w_dir = Y.
# So the rectangle is in X-Z plane, extruded along Y.
# That gives a prism with dimensions: 8.5 along X, 18.0 along Z, 2.5 along Y.
# But the world_bbox_estimate says along_x=0, along_y=0, along_z=0 (unknown).
# We'll just create a box centered at origin with those dimensions.
# To match the frame: the rectangle is on X-Z plane, extruded along Y.
# So we create a rectangle on the XZ plane (normal = Y), then extrude along Y.
# But cadquery's workplane is XY by default. We can use workplane("XZ") or just create a box.
# Simpler: create a box centered at origin with dimensions (8.5, 2.5, 18.0) where:
#   X = 8.5 (u direction)
#   Y = 2.5 (w direction, extrusion)
#   Z = 18.0 (v direction, but v_dir = -Z, so width along Z)
# Actually v_dir = -Z means the v axis points in negative Z. So the rectangle spans from -9.0 to 9.0 in Z.
# Let's just use cq.Workplane("XY").box(8.5, 18.0, 2.5) centered? That would give X=8.5, Y=18.0, Z=2.5.
# But our frame says Y is extrusion direction (2.5), and Z is width (18.0).
# So we need X=8.5, Y=2.5, Z=18.0. That's a box with different orientation.
# Let's use workplane("XZ") to draw rectangle on XZ plane, then extrude along Y.

result = (cq.Workplane("XZ")  # workplane normal to Y, so we draw on XZ plane
          .center(0, 0)        # center at origin
          .rect(8.5, 18.0)     # width along X = 8.5, height along Z = 18.0
          .extrude(2.5)        # extrude along positive Y by 2.5 mm
         )

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0004\\ex2/generated.step")
