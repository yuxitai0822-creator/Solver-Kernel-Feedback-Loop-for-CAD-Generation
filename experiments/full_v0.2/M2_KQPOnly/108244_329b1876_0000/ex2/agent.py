import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: U = X, V = -Z, W = Y
# So the rectangle lies in the X-Z plane (since V is -Z), and extrudes along Y.
# The rectangle corners in UV: start_uv = (121.17356, 31.29955), end_uv = (-0.74644, 290.37955)
# But the dimensions are length_u = 1219.2, width_v = 2590.8.
# The UV coordinates given are just one corner; we need to center or place the rectangle.
# We'll create a rectangle centered at origin with the given dimensions, then extrude.

# Create the rectangle profile in the X-Z plane (since u_dir = X, v_dir = -Z)
# We'll use a workplane on the XZ plane (Y=0) and draw a rectangle centered at origin.
# The rectangle spans length_u along X, width_v along Z (but v_dir is -Z, so width_v along -Z).
# To keep it simple, we'll create the rectangle symmetric about origin.

length_u = 1219.2  # mm
width_v = 2590.8    # mm
extrude_dist = 44.45  # mm

# Build the plate: rectangle on XZ plane, extrude along Y positive direction
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108244_329b1876_0000\\ex2/generated.step")
