import cadquery as cq

# Design Plan: extruded circle (disk) with radius 4.7117 mm and height 12.192 mm
# The profile center is at (5.08, 6.35) in the sketch plane (u,v).
# The extrude direction is +w (which corresponds to +y in world coordinates based on frame).
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# So the sketch plane is XZ (u along X, v along -Z), and extrude along Y.

# Build the circle on the XZ plane (workplane 'XZ' in CadQuery)
result = (
    cq.Workplane("XZ")
    .circle(4.7117)
    .extrude(12.192)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106817_bb28b7aa_0003\\neg_01/generated.step")
