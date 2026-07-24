import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Origin convention: bbox_min_corner, so we place the rectangle starting at (0,0,0) in local frame.
# The rectangle curves define a rectangle from u=-0.746... to u=121.173... and v=31.299... to v=290.379...
# But these are in the original coordinate system (cm scaled by 10 to mm).
# To match the expected spans: length_u = 1219.2 mm, width_v = 2590.8 mm.
# We'll create a rectangle centered at origin for simplicity, then extrude.

# Create the rectangular profile on the XY plane (since u_dir = X, v_dir = -Z, w_dir = Y)
# Actually, we need to align with the frame: u along X, v along -Z, w along Y.
# So the profile lies in the X-Z plane (since u and v axes).
# We'll create a workplane on the XZ plane, draw rectangle, then extrude along Y (w direction).

# Dimensions from design plan:
length_u = 1219.2  # mm
width_v = 2590.8   # mm
extrude_dist = 44.45  # mm

# Build the part
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108244_329b1876_0000\\ex2/generated.step")
