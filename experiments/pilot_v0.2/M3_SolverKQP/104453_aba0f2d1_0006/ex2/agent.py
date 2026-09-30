import cadquery as cq

# Outer rectangle: 50 x 30 (mm)
outer_rect = cq.Workplane("XY").rect(50, 30)

# Inner rectangle: 40 x 20 (mm), offset 5mm from outer edges
inner_rect = cq.Workplane("XY").rect(40, 20)

# Create the rectangular frame profile and extrude 500mm along +Z
result = outer_rect.cut(inner_rect).extrude(500)

# Export to STEP file
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\104453_aba0f2d1_0006\ex2/generated.step")