import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 307.848 mm, width_v = 19.05 mm, extrude_distance = 12.7 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: U = X, V = -Z, W = Y
# So the rectangle lies in the X-Z plane (with V inverted), and extrudes along Y.

# Build the rectangle in the XY plane first, then rotate/translate to match frame.
# Simpler: directly use workplane on XZ plane, but CadQuery workplane is XY by default.
# We'll create a box with the correct dimensions and position it at origin.

# The rectangle in UV: u from 0 to 307.848, v from 0 to 19.05 (but v_dir is -Z, so v=0 is z=0, v=19.05 is z=-19.05)
# Actually the profile curves show start_uv (0, 1.905) to (0,0) etc. The rectangle spans u in [0, 30.7848]? Wait the length_u is 307.848, but the curves show u from 0 to 30.7848? That's a factor of 10 discrepancy.
# Check: curves: start_uv (0,1.905) -> (0,0) -> (30.7848,0) -> (30.7848,1.905) -> (0,1.905). So u range is 0 to 30.7848, v range is 0 to 1.905.
# But dimensions say length_u = 307.848, width_v = 19.05. That's exactly 10x larger.
# The compiler notes say "unit_conversion_applied: cm_to_mm (x10)". So the curves are in cm? Actually the dimensions are in mm after conversion.
# The curves might be in original cm units? But the design plan says unit is mm. The curves show 30.7848 and 1.905, which are 1/10 of the dimensions.
# This suggests the profile curves are in cm (original), and dimensions are in mm after conversion.
# We should use the dimensions from the design plan: length_u = 307.848 mm, width_v = 19.05 mm.
# The extrude distance is 12.7 mm.

# So create a rectangle 307.848 x 19.05 mm, extrude 12.7 mm.
# Frame: u_dir = X, v_dir = -Z, w_dir = Y.
# So the rectangle lies in the X-Z plane (with v along -Z). Extrude along Y.

# We'll create a box centered at origin, then translate so that the min corner is at origin.
# The box dimensions: length_u along X, width_v along Z (but v_dir is -Z, so width_v along -Z means the extent in Z is from -19.05 to 0 if we start at 0).
# Actually the profile curves show v from 0 to 1.905 (in cm) or 0 to 19.05 mm. So v=0 is one edge, v=19.05 is the other.
# Since v_dir = -Z, v=0 corresponds to z=0, v=19.05 corresponds to z=-19.05.
# So the rectangle in 3D: u in [0, 307.848] along X, v in [0, 19.05] along -Z => z in [0, -19.05].
# Extrude along +W = +Y by 12.7 mm.

# So the solid is a box from (0, 0, -19.05) to (307.848, 12.7, 0).

result = cq.Workplane("XY").box(307.848, 12.7, 19.05, centered=(False, False, False)).translate((0, 0, -19.05))
# But wait: box centered=False places the box with min corner at origin? Actually centered=(False,False,False) places the box with one corner at origin and extends in positive directions.
# So box(307.848, 12.7, 19.05, centered=(False,False,False)) creates a box from (0,0,0) to (307.848, 12.7, 19.05).
# We need the box to extend from z=-19.05 to z=0, so we translate by (0,0,-19.05).

result = cq.Workplane("XY").box(307.848, 12.7, 19.05, centered=(False, False, False)).translate((0, 0, -19.05))

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0005\\ex2/generated.step")