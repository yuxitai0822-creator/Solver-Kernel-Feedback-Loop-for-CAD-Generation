import cadquery as cq

# Create a cylinder (extruded circle) based on the design plan.
# The design plan specifies:
# - Circle radius: 12.5 mm (from dimensions.profiles[0].radius, note the value is 12.5 after cm->mm conversion: 1.25 cm = 12.5 mm)
# - Extrude distance: 75.0 mm (from extrude.distance_total.value, already in mm)
# - The circle center in UV is at (-15.0, 10.0) mm (from dimensions.profiles[0].center_uv, after cm->mm: -1.5 cm = -15 mm, 1.0 cm = 10 mm)
# - The frame has u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0).
#   This means the extrusion direction is +w = (1,0,0) in world coordinates.
#   The circle lies in the plane spanned by u and v, i.e., the YZ plane (since u=Z, v=Y).
#   So we create a circle on the YZ plane, centered at (0, -15, 10) in world? Wait: center_uv = (-15,10) in UV coordinates.
#   u_dir = (0,0,-1), v_dir = (0,1,0). So a point (u,v) maps to world: origin + u*u_dir + v*v_dir.
#   The origin is at bbox_min_corner, but we don't have an explicit origin offset. We'll assume the sketch plane passes through world origin.
#   So center in world = (-15)*(0,0,-1) + 10*(0,1,0) = (0, 10, 15).
#   Then extrude along w_dir = (1,0,0) for 75 mm.

# Build the cylinder using a workplane on the YZ plane (which is normal to X axis).
# We'll use a Workplane on the YZ plane (X=0) and then offset the center.

result = (
    cq.Workplane("YZ")
    .circle(12.5)
    .extrude(75.0)
)

# The above creates a cylinder centered at (0,0,0) on the YZ plane, extruded along X.
# But we need the center at (0, 10, 15) in world? Actually the design plan's center_uv is (-15,10) in UV.
# Since u_dir = (0,0,-1), v_dir = (0,1,0), the center in world = (-15)*(0,0,-1) + 10*(0,1,0) = (0, 10, 15).
# So we need to translate the cylinder so that its center is at (0, 10, 15).
# However, the circle is drawn on the YZ plane with center at (0,0) by default. We can use a center point.
# In CadQuery, .circle(radius, center) is not directly available; we can use .center(x,y) before circle.
# On the YZ plane, the coordinates are (Y, Z). So we need to move to (y=10, z=15).

result = (
    cq.Workplane("YZ")
    .center(10, 15)  # move to y=10, z=15
    .circle(12.5)
    .extrude(75.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104283_e5646f96_0000\\neg_03/generated.step")