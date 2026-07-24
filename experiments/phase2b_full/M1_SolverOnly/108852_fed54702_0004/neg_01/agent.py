import cadquery as cq

# Design Plan: extruded circle (disk) with radius 3.96875 mm and height 139.7 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# We'll create a circle in the XY plane (normal = (0,0,1)) and extrude along Z.
# Then rotate/translate to match the specified frame orientation.

# Create the base circle in XY plane
result = (
    cq.Workplane("XY")
    .circle(3.96875)  # radius in mm
    .extrude(139.7)   # extrude along +Z
)

# Now transform to match the frame:
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the local X axis is (1,0,0), local Y is (0,0,-1), local Z is (0,1,0)
# Our current part has X=(1,0,0), Y=(0,1,0), Z=(0,0,1)
# We need to rotate so that original Z becomes Y, and original Y becomes -Z.
# Rotation: new_X = old_X, new_Y = -old_Z, new_Z = old_Y
# This is a rotation of -90 degrees about X axis.

result = result.rotate((0,0,0), (1,0,0), -90)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108852_fed54702_0004\\neg_01/generated.step")
