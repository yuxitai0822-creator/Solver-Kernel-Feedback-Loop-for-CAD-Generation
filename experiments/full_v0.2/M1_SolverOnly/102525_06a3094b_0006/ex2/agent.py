import cadquery as cq

# Design Plan: rectangular prism (SOP-28 body)
# Dimensions: length_u = 11.3 mm, width_v = 21.0 mm, extrude_distance = 3.0 mm
# The profile is a rectangle centered at origin in the uv-plane.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# This means: u -> X, v -> -Z, w -> Y.
# The rectangle in uv coordinates: u from -0.565 to 0.565, v from -1.05 to 1.05.
# But the dimensions say length_u = 11.3, width_v = 21.0.
# The uv coordinates given are half-extents: 0.565 = 11.3/20? Actually 11.3/2 = 5.65, not 0.565.
# There is a note: unit_conversion_applied: cm_to_mm (x10). So the uv values are in cm? 
# The design plan says unit is mm, but the uv coordinates are 0.565 and 1.05.
# If we multiply by 10: 5.65 and 10.5, which are half of 11.3 and 21.0. That matches.
# So the uv coordinates are in cm, but we work in mm. So we scale by 10.
# Alternatively, we can just use the explicit dimensions: length_u=11.3, width_v=21.0.
# The rectangle center is at (0,0) in uv, half-lengths: 11.3/2 = 5.65, 21.0/2 = 10.5.
# In the frame: u -> X, v -> -Z. So the rectangle lies in the XZ plane.
# Extrude direction: +w = +Y, distance = 3.0 mm.

# Build the rectangle in the XZ plane (u=X, v=-Z).
# We'll create a workplane on the Y=0 plane (since extrude starts at w=0).
# The rectangle: center at (0,0,0), width along X = 11.3, height along Z = 21.0.
# But careful: v_dir = (0,0,-1), so positive v maps to negative Z.
# The uv coordinates: v from -1.05 to 1.05 (in cm) -> after scaling: -10.5 to 10.5 mm.
# So the rectangle spans Z from -10.5 to 10.5? Actually v positive -> negative Z.
# v = -1.05 -> Z = 10.5, v = 1.05 -> Z = -10.5. So the rectangle is symmetric about Z=0.
# We'll just use center at origin, size (11.3, 21.0) on the XY plane? No, on XZ.
# Cadquery workplane: by default on XY. We need to work on XZ plane.
# We can use workplane("XZ") or workplane(offset=0, direction=cq.Vector(0,1,0)).
# Let's use workplane("XZ") which gives normal along Y, which matches w_dir = (0,1,0).

result = (cq.Workplane("XZ")
          .rect(11.3, 21.0, centered=True)
          .extrude(3.0))

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102525_06a3094b_0006\\ex2/generated.step")
