import cadquery as cq

# Create a cylinder (extruded circle) with radius 3.0 mm and height 14.0 mm
# The design plan specifies a disk with radius 3.0 (from profile radius) and extrude distance 14.0
# Note: The profile radius in the design plan is 0.3? Actually check: profile radius is 3.0 in dimensions, but curves radius is 0.3? 
# The dimensions section says radius value 3.0, so we use that.

result = cq.Workplane("XY").circle(3.0).extrude(14.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\107467_a8afc51d_0000\\neg_03/generated.step")
