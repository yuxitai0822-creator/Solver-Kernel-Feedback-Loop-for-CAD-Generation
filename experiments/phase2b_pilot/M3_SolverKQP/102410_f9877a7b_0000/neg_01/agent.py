import cadquery as cq

# Build an extruded annulus (bearing-like part)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm
# The design plan specifies the extrude direction as +w, where w_dir is [0, 1, 0],
# meaning the extrusion happens along the Y axis.

result = (
    cq.Workplane("XZ")
    .circle(6.0)
    .circle(4.25)
    .extrude(11.5)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-SolverKQP双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\102410_f9877a7b_0000\neg_01/generated.step"

cq.exporters.export(result, OUT_STEP_PATH)