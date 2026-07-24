import cadquery as cq

# Design Plan: extruded circle (disk) with radius 0.8 mm and height 4.0 mm
# The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the extrusion direction is -w = (0,-1,0) (negative Y in world)
# But for simplicity, we create the circle in the XZ plane and extrude along Y.

# Create a workplane on the XZ plane (normal = Y axis)
# The circle center is at (0,0) in UV, which maps to (0,0) in the plane.
# Radius = 0.8 mm (from profile radius, note the profile curve radius is 0.08 but that's a scaling? 
# Actually the profile curve radius is 0.08, but the explicit dimension says radius = 0.8. 
# The profile curve radius 0.08 seems to be a mistake or scaling factor; we use the explicit dimension 0.8.

radius = 0.8  # mm
height = 4.0  # mm

# Build the disk: circle extruded along Y axis (since w_dir = (0,1,0) and extrude direction is -w)
# We'll extrude in the negative Y direction, but the result is symmetric.
result = (
    cq.Workplane("XZ")
    .circle(radius)
    .extrude(height)  # extrude along Y positive by default; we want 4 mm total
)

# The extrusion direction in the design plan is -w, which is (0,-1,0).
# To match exactly, we can extrude in the negative Y direction by using a negative distance.
# But the absolute distance is 4.0, so we extrude -4.0 in Y.
# However, the Workplane circle is centered at origin, so extruding in either direction gives same shape.
# Let's do it explicitly:
result = (
    cq.Workplane("XZ")
    .circle(radius)
    .extrude(-height)  # extrude 4 mm in negative Y direction
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\102760_26430589_0037\neg_01/generated.step")
