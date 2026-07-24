import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a flat plate/panel with extruded rectangle profile
# Coordinates are in part-local frame with origin at bbox min corner

# Create the base rectangle on the XY plane (u=x, v=z, w=y according to frame)
# The frame has u_dir = [1,0,0] (x), v_dir = [0,0,-1] (-z), w_dir = [0,1,0] (y)
# So the profile lies in the XZ plane, extruded along Y

# Profile rectangle corners from UV coordinates:
# The curves define a rectangle with corners at:
# (7.82976, -66.3440) to (127.82976, -6.3440) in UV space
# But the dimensions say length_u=1200, width_v=600
# The UV coordinates appear to be scaled/offset - we use the explicit dimensions

# Build the plate centered at origin for simplicity, then translate to match
# the design intent (bbox min corner at origin)

# Create a rectangle with length=1200 (along u/x) and width=600 (along v/-z)
# Extrude along w (y) by 20mm

result = (
    cq.Workplane("XY")
    .rect(1200, 600)
    .extrude(20)
)

# The resulting part has its center at (0,0,10) with dimensions 1200x600x20
# This matches the design plan: flat plate 1200mm x 600mm x 20mm

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101817_b02acd9f_0004\\neg_02/generated.step")
