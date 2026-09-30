import cadquery as cq

# Create a rectangular prism with dimensions: length_u=3.9, width_v=4.9, extrude_distance=1.55
# The profile is centered at origin in the uv-plane, then extruded in the +w direction.
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle lies in the X-Z plane (u along X, v along -Z) and extrudes along Y.

# Build the rectangle profile centered at origin in uv coordinates
# uv coordinates: u from -0.195 to 0.195, v from -0.245 to 0.245
# In world: u -> X, v -> -Z, so:
#   X from -0.195 to 0.195
#   Z from -(-0.245)=0.245 to -0.245=-0.245 (i.e., Z from -0.245 to 0.245)

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(0.39, 0.49)  # width=0.39 (2*0.195), height=0.49 (2*0.245)
    .extrude(1.55)  # extrude along Z (default), but we need to rotate to match frame
)

# The above extrudes along Z, but we need extrusion along Y (w_dir).
# So we rotate the result: align Z to Y.
# Rotate 90 degrees around X axis: Z -> -Y? Let's check:
#   Rotation of 90 deg around X: (x,y,z) -> (x, -z, y)
#   So Z becomes Y, Y becomes -Z. We want Z to become Y, so this works.
result = result.rotate((0,0,0), (1,0,0), -90)

# Now the part is oriented correctly: u along X, v along -Z, w along Y.
# Dimensions: X span = 0.39, Z span = 0.49, Y span = 1.55
# But the design plan expects: length_u=3.9, width_v=4.9, extrude_distance=1.55
# The uv coordinates were given as 0.195 and 0.245, but the dimensions say 3.9 and 4.9.
# This suggests the uv coordinates are in cm (0.195 cm = 1.95 mm, 0.245 cm = 2.45 mm)
# But the dimensions are in mm: 3.9 mm and 4.9 mm.
# Actually, the compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
# So the uv coordinates were originally in cm and multiplied by 10 to get mm.
# 0.195 cm * 10 = 1.95 mm, but 3.9 mm is the full length, so half-length is 1.95 mm. Correct.
# 0.245 cm * 10 = 2.45 mm, half of 4.9 mm. Correct.
# So the rectangle should be 3.9 mm x 4.9 mm, extruded 1.55 mm.

# Rebuild with correct dimensions:
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(3.9, 4.9)  # width=3.9, height=4.9
    .extrude(1.55)
)

# Rotate to match frame: u->X, v->-Z, w->Y
# The rectangle is in XY plane, extrudes along Z.
# We want rectangle in XZ plane (u along X, v along -Z), extrude along Y.
# Rotate -90 deg around X: (x,y,z) -> (x, z, -y)  Wait, let's be precise.
# Standard rotation matrix R_x(-90):
# [1, 0, 0; 0, cos(-90), -sin(-90); 0, sin(-90), cos(-90)]
# = [1, 0, 0; 0, 0, 1; 0, -1, 0]
# So (x, y, z) -> (x, z, -y)
# Original: rect in XY, extrude along Z -> (x, y, 0 to 1.55)
# After rotation: (x, z, -y) -> x stays, y becomes z, z becomes -y
# So the rectangle is now in XZ plane (x and z vary), and the extrusion is along -Y.
# But we want extrusion along +Y (w_dir = [0,1,0]).
# So we need to rotate 90 deg around X instead:
# R_x(90): [1, 0, 0; 0, 0, -1; 0, 1, 0]
# (x, y, z) -> (x, -z, y)
# Original: rect in XY, extrude along Z -> (x, y, 0 to 1.55)
# After: (x, -z, y) -> x stays, y becomes -z, z becomes y
# So rectangle in X(-Z) plane? Actually y becomes -z, so the rectangle's y coordinate becomes -z.
# The rectangle's y range is -2.45 to 2.45, so z range becomes -2.45 to 2.45 (after negation).
# The extrusion along Z becomes along Y (since z becomes y).
# So the rectangle is in XZ plane (x and z vary), extruded along Y.
# But v_dir is [0,0,-1], meaning v is along -Z. Our rectangle's v (height) was along Y originally,
# now becomes -Z. So v is along -Z. Correct.

result = result.rotate((0,0,0), (1,0,0), 90)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0000\\neg_03/generated.step")