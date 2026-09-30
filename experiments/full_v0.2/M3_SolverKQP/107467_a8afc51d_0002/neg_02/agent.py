import cadquery as cq

# Create a cylinder (extruded circle) with radius 3.0 mm and height 25.0 mm
# The design plan specifies a disk/cylinder with radius 3.0 (from profile radius)
# and extrude distance 25.0 mm along +w direction.
# Note: The profile circle radius is 0.3 in the curves section, but the dimensions
# section clearly states radius = 3.0 mm. The 0.3 appears to be a scaling artifact
# from cm->mm conversion (0.3 cm = 3.0 mm). We use the explicit dimension value.

result = cq.Workplane("XY").circle(3.0).extrude(25.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107467_a8afc51d_0002\\neg_02/generated.step")
