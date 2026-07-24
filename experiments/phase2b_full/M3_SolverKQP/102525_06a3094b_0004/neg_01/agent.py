import cadquery as cq

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin in the u-v plane.
# u direction = (1,0,0), v direction = (0,0,-1), w direction = (0,1,0)
# Extrude in +w direction (positive y) by 2.5 mm.

# Create the rectangle profile centered at origin
# Width along u (x) = 8.5 mm, length along v (z negative) = 18.0 mm
# The rectangle vertices from the plan: u from -0.425 to 0.425, v from -0.9 to 0.9
# But those are half-dimensions? Actually the plan says length_u=8.5, width_v=18.0
# The uv coordinates given: start_uv = [0.425, -0.9] etc. So half extents are 0.425 and 0.9
# That would give total u span = 0.85, v span = 1.8 — but the dimensions say 8.5 and 18.0.
# The plan notes unit_conversion_applied: cm_to_mm (x10). So the uv values are in cm?
# Actually the plan says unit is mm, but the uv coordinates are 0.425, 0.9 etc.
# The dimensions say 8.5 and 18.0 mm. So the uv coordinates are half-dimensions in mm?
# 0.425*2 = 0.85, not 8.5. So there's a factor of 10 discrepancy.
# The plan says "unit_conversion_applied: cm_to_mm (x10)". So original was in cm, converted to mm.
# The uv coordinates might be in the original cm units? Or the dimensions are already in mm.
# The dimensions say value=8.5, source=explicit_dimension, unit=mm.
# The uv coordinates: 0.425 cm = 4.25 mm, 0.9 cm = 9.0 mm. Then half extents: 4.25 and 9.0 mm.
# Total u span = 8.5 mm, v span = 18.0 mm. That matches!
# So the uv coordinates are in cm (original), but we need to use mm.
# Convert: multiply uv by 10 to get mm.

# So half extents in mm: u_half = 0.425 * 10 = 4.25, v_half = 0.9 * 10 = 9.0
# Rectangle corners in mm: (-4.25, -9.0), (4.25, -9.0), (4.25, 9.0), (-4.25, 9.0)
# But note: v direction is (0,0,-1), so v coordinate maps to -z.
# In the uv plane: u -> x, v -> -z (since v_dir = (0,0,-1))
# So rectangle in xz plane: x from -4.25 to 4.25, z from -9.0 to 9.0 (since v=-z, v=-9 -> z=9, v=9 -> z=-9)
# Actually careful: v coordinate goes from -0.9 to 0.9 (in cm), so in mm v from -9 to 9.
# v_dir = (0,0,-1), so point = u*u_dir + v*v_dir = (u, 0, -v)
# So when v = -9, z = 9; when v = 9, z = -9.
# So the rectangle spans x: [-4.25, 4.25], z: [-9, 9] (but reversed order).
# For simplicity, create a rectangle centered at origin in xz plane.

# Extrude in +w direction = (0,1,0) by 2.5 mm.

# Build the result
result = (cq.Workplane("XZ")
          .center(0, 0)
          .rect(8.5, 18.0)
          .extrude(2.5))

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0004\\neg_01/generated.step")
