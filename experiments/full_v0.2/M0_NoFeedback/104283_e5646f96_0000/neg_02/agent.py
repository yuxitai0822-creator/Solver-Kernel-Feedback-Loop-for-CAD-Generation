import cadquery as cq

# Design Plan: extruded circle (disk/shaft)
# Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
# Extrude: 75.0 mm along +w direction (which maps to world X axis)
# Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# So in CadQuery: sketch on YZ plane (normal = X), then extrude along +X

# Create workplane on YZ plane (normal = (1,0,0))
result = cq.Workplane("YZ").circle(12.5).extrude(75.0)

# The design specifies center at (-15.0, 10.0) in UV coordinates.
# In our workplane YZ, U maps to -Z, V maps to Y.
# So center_uv = (-1.5, 1.0) in design plan (scaled by 10 from cm to mm?)
# Actually dimensions: radius=12.5, center_uv=[-15.0, 10.0] in mm.
# In YZ plane: Y = V = 10.0, Z = -U = 15.0 (since u_dir = (0,0,-1))
# So we need to position the circle at (Y=10, Z=15)

result = cq.Workplane("YZ").center(10.0, 15.0).circle(12.5).extrude(75.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104283_e5646f96_0000\\neg_02/generated.step")
