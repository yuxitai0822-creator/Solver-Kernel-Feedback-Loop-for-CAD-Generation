import cadquery as cq

# Design Plan: thumb screw (disk)
# Profile: circle with radius 4.87045 mm, center at (114.300004, 0.0) in UV
# Extrude: 6.8707 mm in +w direction
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# The circle center in UV is (114.300004, 0.0). In the local frame, this means
# the circle is offset along the u-axis by 114.300004 mm.
# However, the dimensions section gives radius=4.87045 and center_uv=[114.300004, 0.0].
# The span along u and v is expected to be 9.7409 (diameter = 2*4.87045 = 9.7409).
# This suggests the circle is centered at (114.300004, 0.0) in the sketch plane.
# We'll create a workplane on the XY plane (since u_dir = X, v_dir = -Z, w_dir = Y).
# Actually, v_dir = (0,0,-1) means the sketch plane normal is along w_dir = (0,1,0).
# So the sketch plane is the XZ plane (normal Y). But v_dir is (0,0,-1) which is -Z.
# So the sketch axes: u = X, v = -Z. The circle center is at (114.300004, 0.0) in (u,v).
# That means in 3D: X = 114.300004, Z = 0 (since v=0).
# Extrude direction is +w = +Y.

# Build the result:
result = (
    cq.Workplane("XZ")
    .circle(4.87045)
    .extrude(6.8707)
)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106817_bb28b7aa_0002\\ex2/generated.step")
