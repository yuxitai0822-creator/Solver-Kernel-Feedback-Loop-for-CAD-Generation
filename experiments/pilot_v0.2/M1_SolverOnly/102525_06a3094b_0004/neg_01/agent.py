import cadquery as cq

# Build a rectangular prism representing an SOP-28 package
# Dimensions: 8.5mm (u) x 18.0mm (v) x 2.5mm (w)
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
# Origin convention: bbox_min_corner

result = (
    cq.Workplane("XY")
    .rect(8.5, 18.0)
    .extrude(2.5)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\102525_06a3094b_0004\neg_01/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)