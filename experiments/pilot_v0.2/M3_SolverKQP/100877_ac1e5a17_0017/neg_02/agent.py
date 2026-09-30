import cadquery as cq

# Build a flat plate/panel: extruded rectangle
# Dimensions: 254.0 mm (u) x 190.5 mm (v) x 3.175 mm (w)
# Origin at bbox_min_corner

result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\100877_ac1e5a17_0017\neg_02/generated.step"

cq.exporters.export(result, OUT_STEP_PATH)