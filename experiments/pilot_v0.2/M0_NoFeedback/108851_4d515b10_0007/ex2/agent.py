import cadquery as cq

# Build a rectangular box: 279.4 mm (X) x 50.8 mm (Z) x 19.05 mm (Y)
# The design plan specifies a rectangle in the UV plane (X, -Z) extruded along W (+Y).
# We use a standard XZ workplane and extrude along +Y to match the frame axes.

result = (
    cq.Workplane("XZ")
    .rect(279.4, 50.8)
    .extrude(19.05)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\108851_4d515b10_0007\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)