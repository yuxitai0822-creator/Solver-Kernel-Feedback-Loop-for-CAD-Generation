import cadquery as cq

# Build a flat plate/panel: extruded rectangle
# Dimensions: 279.4 mm (u) x 215.9 mm (v) x 1.5875 mm (w)
# Origin at bbox_min_corner

result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\100877_ac1e5a17_0001\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
