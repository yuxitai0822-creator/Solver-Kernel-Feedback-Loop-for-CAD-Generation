import cadquery as cq

# Create a rectangular frame by extruding a rectangular profile with a hole
# Outer rectangle: 40mm x 40mm (from u: 6 to 10, v: -7 to -3 -> span 4 in u and 4 in v? Wait, let's recalc)
# Actually from the curves: outer ring goes from (10,-7) to (6,-7) to (6,-3) to (10,-3) back to (10,-7)
# That's a rectangle of width 4 in u and height 4 in v. But dimensions say outer_length_u=40, outer_width_v=40.
# The coordinates are in a local frame with u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0).
# The span in u is from 6 to 10 = 4 units, but the design says 40mm. So scale factor 10? 
# The compiler notes say cm_to_mm (x10). So the coordinates in the plan are in cm, we need to convert to mm by multiplying by 10.
# So outer rectangle: u from 60 to 100, v from -70 to -30 (but v_dir is (0,0,-1), so v coordinate negative means positive z?)
# Let's just build the shape in the local frame and then transform.

# Define the local frame axes
u_dir = (1.0, 0.0, 0.0)  # x-axis
v_dir = (0.0, 0.0, -1.0) # negative z-axis
w_dir = (0.0, 1.0, 0.0)  # y-axis

# The profile is in the uv-plane. We'll create a 2D sketch in the plane defined by u and v.
# The plane normal is w_dir = (0,1,0) (y-axis). So the sketch plane is XZ (since u=x, v=-z).
# But cadquery's workplane is easier: we can create a box and subtract a smaller box.

# Outer dimensions: 40mm x 40mm (after scaling from cm to mm)
outer_u = 40.0  # mm
outer_v = 40.0  # mm
# Inner dimensions: 37.6mm x 37.6mm
inner_u = 37.6  # mm
inner_v = 37.6  # mm
# Extrude distance: 780mm along w (y-axis)
extrude_dist = 780.0  # mm

# Build the frame as a box with a hole through it
# We'll create a solid box of outer dimensions, then subtract a smaller box for the hole.
# The frame is centered? The profile coordinates suggest the outer rectangle goes from u=60 to 100 (center at 80) and v=-70 to -30 (center at -50).
# But the dimensions say outer_length_u=40, outer_width_v=40. So the coordinates in the plan are in cm, and the actual size is 40mm.
# The center of the outer rectangle in uv coordinates: u_center = (60+100)/2 = 80, v_center = (-70-30)/2 = -50.
# But after scaling to mm, the center is at (80*10? No, the plan says the coordinates are already in mm? 
# The unit is mm, but the compiler notes say cm_to_mm (x10). So the numbers in the plan are in cm, we need to multiply by 10 to get mm.
# So outer rectangle: u from 100 to 60? Actually start_uv (10,-7) means 10cm = 100mm, -7cm = -70mm.
# So outer rectangle corners in mm: (100, -70), (60, -70), (60, -30), (100, -30).
# That's a rectangle of width 40mm in u and height 40mm in v. Center at (80, -50).
# Inner rectangle corners: (61.2, -68.8), (61.2, -31.2), (98.8, -31.2), (98.8, -68.8).
# That's width 37.6mm and height 37.6mm. Center at (80, -50).

# So the frame is centered at (80, -50) in uv-plane, with outer 40x40 and inner 37.6x37.6.
# We'll create the profile centered at origin for simplicity, then translate.

# Create the outer rectangle centered at origin
outer = cq.Workplane("XY").rect(40.0, 40.0).extrude(extrude_dist)
# Create the inner rectangle centered at origin
inner = cq.Workplane("XY").rect(37.6, 37.6).extrude(extrude_dist)
# Subtract inner from outer to get the frame
result = outer.cut(inner)

# Now we need to orient the frame according to the local frame:
# u_dir = x-axis, v_dir = -z-axis, w_dir = y-axis.
# Our current result has its profile in XY plane and extrudes along Z.
# We need to rotate so that the profile plane is XZ (u=x, v=-z) and extrude along Y (w).
# Actually, we built the box with profile in XY and extrude along Z. 
# To match the local frame: u=x, v=-z, w=y.
# So we need to rotate the result: the profile should be in the XZ plane, extrude along Y.
# Our current result has profile in XY, extrude along Z. 
# We can rotate 90 degrees around X axis to bring XY to XZ? 
# Rotate -90 around X: (x,y,z) -> (x, z, -y). Then profile in XY becomes in XZ? 
# Let's just use a workplane approach with proper orientation.

# Better approach: create the sketch on a workplane oriented correctly.
# The profile plane is defined by u and v axes. u_dir = (1,0,0), v_dir = (0,0,-1).
# So the plane normal is u_dir cross v_dir = (1,0,0) x (0,0,-1) = (0,1,0) = w_dir.
# So the sketch plane has normal (0,1,0), i.e., the Y-axis.
# In cadquery, we can use Workplane("YZ") or Workplane("XZ") and rotate.
# Actually, a plane with normal (0,1,0) is the XZ plane (Y is normal).
# So we can use Workplane("XZ") and draw the profile.

# Let's rebuild properly:
result = (
    cq.Workplane("XZ")
    .center(80.0, -50.0)  # center of the profile in uv coordinates (u=x, v=z? Wait, v_dir = -z, so v coordinate maps to -z)
    # Actually, on Workplane("XZ"), x is x, z is z. But v_dir = -z, so v coordinate = -z.
    # So center at (u=80, v=-50) means x=80, z=50 (since v=-z => z=-v=50).
    .rect(40.0, 40.0)
    .extrude(extrude_dist)  # extrudes along Y (normal to XZ plane)
)

# Now subtract the inner hole
inner_hole = (
    cq.Workplane("XZ")
    .center(80.0, 50.0)  # inner center same as outer center: u=80, v=-50 => x=80, z=50
    .rect(37.6, 37.6)
    .extrude(extrude_dist)
)

result = result.cut(inner_hole)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0000\\neg_02/generated.step")
