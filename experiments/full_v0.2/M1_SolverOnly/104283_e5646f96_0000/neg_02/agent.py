import cadquery as cq

# Design Plan: extruded circle (disk)
# Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
# Extrude: 75.0 mm along +w direction (which is world X axis based on frame)
# Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# So in CadQuery: workplane on XY, then transform to align with frame

# Build the circle on a workplane aligned to the frame
# The frame's u,v,w correspond to local X,Y,Z in CadQuery after rotation
# We'll create a workplane on the XY plane, then rotate to match frame
# Frame: u = -Z, v = Y, w = X
# So we can use workplane("XY") and then rotate appropriately

# Simpler: create a circle at the correct position in 3D space
# The profile center_uv = (-15.0, 10.0) in UV coordinates
# In world: center = u*center_u + v*center_v = (-15.0)*u_dir + 10.0*v_dir
# u_dir = (0,0,-1), v_dir = (0,1,0)
# center = (-15.0)*(0,0,-1) + 10.0*(0,1,0) = (0, 10, 15.0)

center = (0.0, 10.0, 15.0)
radius = 12.5

# Create workplane on XY plane, then move to center and create circle
# The extrusion direction is +w = (1,0,0) which is X axis
# So we need the circle to be on a plane perpendicular to X axis
# That means workplane on YZ plane

result = (
    cq.Workplane("YZ")
    .center(center[1], center[2])  # center in YZ plane: (y, z)
    .circle(radius)
    .extrude(75.0)  # extrude along X (positive)
)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104283_e5646f96_0000\\neg_02/generated.step")
