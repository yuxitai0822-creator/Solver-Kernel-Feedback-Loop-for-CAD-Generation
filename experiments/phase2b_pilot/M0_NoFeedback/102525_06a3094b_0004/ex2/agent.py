import cadquery as cq

# Build a rectangular prism for SOP-28 (1)
# Dimensions: 8.5 mm (u) x 18.0 mm (v) x 2.5 mm (w)
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# Origin convention: bbox_min_corner

result = (
    cq.Workplane("XZ")
    .rect(8.5, 18.0)
    .extrude(2.5)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\102525_06a3094b_0004\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)