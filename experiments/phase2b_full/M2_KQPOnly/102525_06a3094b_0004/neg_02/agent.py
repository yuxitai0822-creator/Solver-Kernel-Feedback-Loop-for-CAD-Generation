import cadquery as cq

# Create a rectangular prism with dimensions:
# length_u = 8.5 mm (along x-axis)
# width_v = 18.0 mm (along z-axis, since v_dir = [0,0,-1])
# extrude_distance = 2.5 mm (along y-axis, since w_dir = [0,1,0])

# The profile is centered at origin in uv plane.
# u ranges from -4.25 to 4.25, v ranges from -9.0 to 9.0
# Then extrude in +w direction (y-axis) by 2.5 mm

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(8.5, 18.0)
    .extrude(2.5)
)

cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102525_06a3094b_0004\\neg_02/generated.step")
