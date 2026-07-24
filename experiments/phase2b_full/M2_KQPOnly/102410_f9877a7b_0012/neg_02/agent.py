import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm

# Create the outer cylinder
outer_cylinder = cq.Workplane("XY").circle(6.0).extrude(12.0)

# Create the inner cylinder (to be subtracted)
inner_cylinder = cq.Workplane("XY").circle(4.25).extrude(12.0)

# Subtract inner from outer to create the annulus
result = outer_cylinder.cut(inner_cylinder)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102410_f9877a7b_0012\\neg_02/generated.step")
