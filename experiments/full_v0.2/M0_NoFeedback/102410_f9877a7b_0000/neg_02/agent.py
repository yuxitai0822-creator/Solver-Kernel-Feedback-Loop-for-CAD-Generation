import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm

# Create the outer cylinder
outer_cylinder = cq.Workplane("XY").circle(6.0).extrude(11.5)

# Create the inner cylinder (hole)
inner_cylinder = cq.Workplane("XY").circle(4.25).extrude(11.5)

# Subtract inner from outer to create the annulus
result = outer_cylinder.cut(inner_cylinder)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102410_f9877a7b_0000\neg_02/generated.step")
