import cadquery as cq

# Create the outer rectangle profile
outer = cq.Workplane("XY").rect(1980.0, 600.0).extrude(25.0)

# Create the inner rectangle profile (the hole)
inner = cq.Workplane("XY").rect(1930.0, 550.0).extrude(25.0)

# Subtract inner from outer to create the frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101427_a9bcb09c_0001\\neg_02/generated.step")
