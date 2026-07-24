import cadquery as cq

# Create a cylinder (extruded circle) with radius 3.0 mm and height 14.0 mm
# The design plan specifies a disk (extruded circle) with radius 3.0 and extrude distance 14.0
# The coordinate system is part_local with origin at bbox_min_corner, so we center the circle at (0,0)
# and extrude in the +w direction (which is +z in the local frame)

result = cq.Workplane("XY").circle(3.0).extrude(14.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\107467_a8afc51d_0000\\neg_02/generated.step")
