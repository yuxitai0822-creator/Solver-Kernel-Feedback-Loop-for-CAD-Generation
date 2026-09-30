import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle in the UV plane, where:
#   U direction = (1,0,0) i.e. X axis
#   V direction = (0,0,-1) i.e. negative Z axis
#   W direction = (0,1,0) i.e. Y axis (extrude direction)
#
# Profile rectangle corners in UV coordinates:
#   (0,0), (9.525,0), (9.525,57.15), (0,57.15)
# These are in the UV plane, but we need to map to 3D.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# So a point (u,v) maps to: origin + u*u_dir + v*v_dir.
# The origin is at bbox_min_corner, which we can set to (0,0,0) for simplicity.
#
# The rectangle dimensions: length_u = 95.25, width_v = 571.5
# But the profile curves show coordinates up to 9.525 in u and 57.15 in v.
# This suggests the profile is a unit rectangle scaled by 9.525 in u and 57.15 in v.
# Actually, looking at the curves:
#   start_uv = (9.525, 57.15) to end_uv = (9.525, 0)  -> vertical line at u=9.525
#   start_uv = (0, 57.15) to end_uv = (9.525, 57.15) -> horizontal line at v=57.15
#   start_uv = (0, 0) to end_uv = (0, 57.15) -> vertical line at u=0
#   start_uv = (9.525, 0) to end_uv = (0, 0) -> horizontal line at v=0
# So the rectangle spans u in [0, 9.525] and v in [0, 57.15].
# But the dimensions say length_u = 95.25 and width_v = 571.5.
# This is a factor of 10 difference. The compiler notes say "cm_to_mm (x10)".
# So the profile coordinates are in cm? Actually 9.525*10 = 95.25, 57.15*10 = 571.5.
# So the profile is in cm, but we need to output in mm. We'll scale by 10.
#
# Alternatively, we can just use the dimensions directly: 95.25 mm x 571.5 mm.
# The extrude distance is 19.05 mm.

# Build the rectangle in the XY plane (since u_dir = X, v_dir = -Z, we need to rotate)
# Actually, let's build in the XZ plane and then rotate.
# Simpler: build a rectangle in XY plane, extrude in Z, then rotate to match frame.
# But the frame has w_dir = (0,1,0), so extrude direction is Y.
# Let's build the profile in the XZ plane (u along X, v along -Z).

# Create the rectangle profile in the XZ plane
# u goes from 0 to 95.25 (X direction)
# v goes from 0 to 571.5, but v_dir = (0,0,-1), so v maps to -Z
# So point (u,v) maps to (u, 0, -v)
# Rectangle corners: (0,0,0), (95.25,0,0), (95.25,0,-571.5), (0,0,-571.5)

# Build the wire
pts = [
    (0, 0, 0),
    (95.25, 0, 0),
    (95.25, 0, -571.5),
    (0, 0, -571.5),
    (0, 0, 0)  # close
]

wire = cq.Workplane("XY").polyline(pts).close().wire()

# Create a face from the wire
face = cq.Face.makeFromWires(wire)

# Extrude in the +w direction = (0,1,0) i.e. Y axis
result = cq.Solid.extrudeLinear(face, (0, 19.05, 0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101269_f084ba14_0023\\neg_02/generated.step")
