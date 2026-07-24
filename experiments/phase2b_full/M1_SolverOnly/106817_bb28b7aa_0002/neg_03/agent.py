import cadquery as cq

# Design Plan: thumb screw (disk)
# Extruded circle with radius 4.87045 mm and height 6.8707 mm
# The profile circle center is at (11.43, 0) in UV, but in part-local frame
# we place the circle at origin (0,0) and extrude along Z.

# Create the circular profile
result = (
    cq.Workplane("XY")
    .circle(4.87045)  # radius from design plan
    .extrude(6.8707)   # height from design plan
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106817_bb28b7aa_0002\\neg_03/generated.step")
