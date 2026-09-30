import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 40 x 40 mm (in u-v plane)
# Inner rectangle: 37.6 x 37.6 mm (wall thickness ~1.2 mm)
# Extrude along w direction by 780 mm

# Define the outer rectangle points (u, v) in the local frame
# u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Outer rectangle corners (u, v): (10, -7) -> (6, -7) -> (6, -3) -> (10, -3)
# This gives a 4x4 square? Actually span: u from 6 to 10 => 4, v from -7 to -3 => 4
# But dimensions say outer_length_u = 40, outer_width_v = 40.
# The coordinates in the plan are in a local UV space scaled by 10? 
# The plan says unit_conversion_applied: cm_to_mm (x10). So the UV values are in cm, need to multiply by 10.
# Let's verify: outer rectangle u: 6 to 10 => 4 cm = 40 mm. v: -7 to -3 => 4 cm = 40 mm. Correct.
# Inner rectangle u: 6.12 to 9.88 => 3.76 cm = 37.6 mm. v: -6.88 to -3.12 => 3.76 cm = 37.6 mm. Correct.

# Build the profile in the XY plane (since we'll transform later)
# We'll construct the frame in 2D then extrude along Z, then rotate/translate to match frame axes.

# Step 1: Create the outer rectangle (centered at origin for convenience)
# Outer: width=40, height=40
outer = cq.Workplane("XY").rect(40, 40).extrude(780)

# Step 2: Create the inner rectangle (hole) and subtract
inner = cq.Workplane("XY").rect(37.6, 37.6).extrude(780)

# Step 3: Subtract inner from outer to get hollow frame
result = outer.cut(inner)

# The result is a hollow box centered at origin, extruded along Z.
# But the design plan specifies frame axes: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# This means the extrusion direction (w) is along Y axis, and the profile plane is XZ (u along X, v along -Z).
# Our current result has extrusion along Z. We need to rotate so that:
# - The profile normal (originally Z) aligns with w_dir = (0,1,0) i.e. Y axis
# - u_dir = (1,0,0) stays X
# - v_dir = (0,0,-1) means the v axis in the profile maps to -Z
# Our profile was in XY plane: u = X, v = Y. We need v to map to -Z.
# So we need to rotate: X->X, Y->-Z, Z->Y. That's a rotation of -90 deg around X axis.
# Rotate the result: rotate about X axis by -90 degrees.
result = result.rotate((0,0,0), (1,0,0), -90)

# Now the box extends along Y (w direction) from -390 to 390, centered at origin.
# The profile is in XZ plane: u along X, v along -Z (since Y->-Z after rotation).
# The outer rectangle spans X from -20 to 20, Z from -20 to 20 (since v was -7 to -3 in cm = -70 to -30 mm? Wait, need to check centering)
# Actually our rect(40,40) is centered at origin, so X: -20 to 20, Y: -20 to 20 before rotation.
# After rotation, Y becomes -Z, so Z: -20 to 20. But the design plan has v from -70 to -30 mm (since -7 to -3 cm).
# That means the profile is not centered at origin; it's offset in v direction.
# The plan's outer rectangle v range: -7 to -3 cm = -70 to -30 mm. Center at -50 mm.
# Our current result has v (now Z) centered at 0. We need to shift it.
# Let's adjust: we need the profile to be at v = -50 mm (center). So translate along Z by -50 mm.
result = result.translate((0, 0, -50))

# Now the outer rectangle spans Z from -70 to -30 mm, matching the plan.
# The inner rectangle spans Z from -68.8 to -31.2 mm (since 37.6/2 = 18.8, center at -50 => -68.8 to -31.2).
# Plan inner v: -6.88 to -3.12 cm = -68.8 to -31.2 mm. Correct.

# The extrusion distance is 780 mm along w (Y axis). Our result extends from -390 to 390 along Y.
# The plan doesn't specify a specific position along w, so centered is fine.

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0000\\neg_03/generated.step")