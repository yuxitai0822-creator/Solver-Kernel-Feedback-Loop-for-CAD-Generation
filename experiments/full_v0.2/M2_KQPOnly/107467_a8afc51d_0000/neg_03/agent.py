import cadquery as cq

# Create a cylinder (extruded circle) with radius 3.0 mm and height 14.0 mm
# The design plan specifies a disk (extruded circle) with radius 3.0 and extrude distance 14.0
# Using the part_local coordinate system with origin at bbox_min_corner

# Create the cylinder by extruding a circle
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius from design plan: 3.0 mm (note: profile radius is 3.0, not 0.3 which was in curves radius)
    .extrude(14.0)  # extrude distance from design plan: 14.0 mm
)

# Export to STEP file
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\107467_a8afc51d_0000\\neg_03/generated.step")
