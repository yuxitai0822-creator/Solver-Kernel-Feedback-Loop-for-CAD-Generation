import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u-direction) = 1219.2 mm, Width (v-direction) = 2590.8 mm, Extrude distance (w-direction) = 44.45 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle lies in the X-Z plane (u-v plane) and extrudes along Y (w direction)

# Create the rectangle profile in the X-Z plane
# The profile vertices in uv coordinates: 
#   start_uv = (121.17356129030935, 31.299551148092803)
#   end_uv = (-0.7464387096940412, 31.299551148092803)  -> this is the other corner
# Actually the curves define a rectangle with corners:
#   (121.17, 31.30), (-0.75, 31.30), (-0.75, 290.38), (121.17, 290.38)
# So the rectangle spans from u=-0.746 to u=121.174 (length = 121.92 cm = 1219.2 mm)
# and v=31.30 to v=290.38 (width = 259.08 cm = 2590.8 mm)
# But note: the design plan says length_u = 1219.2, width_v = 2590.8
# The uv coordinates appear to be in cm (since unit_conversion_applied: cm_to_mm x10)
# So we need to multiply by 10 to get mm

# Actually, let's just use the explicit dimensions from the design plan:
length_u = 1219.2  # mm
width_v = 2590.8   # mm
extrude_dist = 44.45  # mm

# The rectangle center in uv space: 
# u_center = (121.17356129030935 + (-0.7464387096940412)) / 2 = 60.21356129030765
# v_center = (31.299551148092803 + 290.379551148076) / 2 = 160.8395511480844
# These are in cm, so in mm: u_center_mm = 602.1356129030765, v_center_mm = 1608.395511480844

# But we can just create the rectangle centered at origin for simplicity
# The design plan uses bbox_min_corner origin convention, but we can place it anywhere
# as long as dimensions are correct

# Create the rectangle in the X-Z plane (u=X, v=-Z, so v direction is negative Z)
# To match the frame: u_dir = X, v_dir = -Z, w_dir = Y
# So the profile is in the X-Z plane, extruded along Y

# Create a workplane on the XZ plane (which is Y=0 plane in CadQuery)
# But CadQuery's XZ plane has normal in Y direction
result = (cq.Workplane("XZ")
          .rect(length_u, width_v, centered=True)
          .extrude(extrude_dist))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108244_329b1876_0000\\neg_01/generated.step")
