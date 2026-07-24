import cadquery as cq

# Design Plan: thumb screw (disk)
# Extruded circle with radius 4.87045 mm and height 6.8707 mm
# The profile circle center is at (11.43, 0) in UV, but we place it at origin for simplicity
# The frame has u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# This means the extrusion direction is +w = (0,1,0) (Y-axis)
# The circle lies in the X-Z plane (u-v plane: u=X, v=-Z)

radius = 4.87045
height = 6.8707

# Build the result: a cylinder along Y-axis
result = (
    cq.Workplane("XZ")
    .circle(radius)
    .extrude(height)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106817_bb28b7aa_0002\\neg_02/generated.step")
