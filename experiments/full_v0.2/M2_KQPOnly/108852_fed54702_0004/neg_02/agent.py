import cadquery as cq

# Design Plan: extruded circle (disk) with radius 3.96875 mm and height 139.7 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# We'll create the circle on the XY plane (normal = (0,0,1)) and extrude along Z.
# To match the frame orientation, we can rotate the result.

# Step 1: Create the base circle on XY plane
radius = 3.96875
height = 139.7

# Create circle at origin, extrude along +Z
result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(height)
)

# The frame in the design plan has:
#   u_dir = (1,0,0)  -> X
#   v_dir = (0,0,-1) -> -Z
#   w_dir = (0,1,0)  -> Y
# Our current result has:
#   u_dir = (1,0,0)  -> X
#   v_dir = (0,1,0)  -> Y
#   w_dir = (0,0,1)  -> Z
# We need to rotate so that v_dir becomes (0,0,-1) and w_dir becomes (0,1,0).
# This is a rotation of -90 degrees around X axis.
result = result.rotate((0,0,0), (1,0,0), -90)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\108852_fed54702_0004\neg_02/generated.step")
