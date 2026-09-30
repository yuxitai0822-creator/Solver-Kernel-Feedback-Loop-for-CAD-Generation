import cadquery as cq

# Create a cylinder (extruded circle) with radius 3.0 mm and height 25.0 mm
# The design plan specifies a disk (extruded circle) with radius 3.0 mm and extrude distance 25.0 mm
# The profile is a circle of radius 0.3 (in UV space) but the actual radius is 3.0 mm (from dimensions)
# The UV radius 0.3 is likely a normalized value; we use the explicit dimension radius = 3.0 mm

# Create the cylinder by extruding a circle
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius in mm
    .extrude(25.0)  # height in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\107467_a8afc51d_0002\\neg_03/generated.step")
