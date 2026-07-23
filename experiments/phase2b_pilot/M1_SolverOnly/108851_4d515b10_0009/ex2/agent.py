import cadquery as cq

# Build an extruded rectangle (flat plate/panel)
# Profile dimensions: length_u = 209.55 mm, width_v = 57.912 mm
# Extrude distance: 19.05 mm along +Y (w_dir)

result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\108851_4d515b10_0009\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)