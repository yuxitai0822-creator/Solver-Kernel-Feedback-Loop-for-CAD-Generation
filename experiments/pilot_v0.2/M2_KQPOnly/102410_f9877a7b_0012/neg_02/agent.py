import cadquery as cq

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\102410_f9877a7b_0012\neg_02/generated.step"

# Create an extruded annulus (bearing cross-section)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
result = (
    cq.Workplane("XY")
    .circle(6.0)
    .circle(4.25)
    .extrude(12.0)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)