import cadquery as cq

# Build the extruded rectangle for SoapCutterBackBar1 v1
# Profile: rectangle 27.94 x 5.08 (in cm, converted to mm: 279.4 x 50.8)
# Extrude distance: 19.05 mm along +Y (w_dir)
# Frame: u_dir=[1,0,0] (X), v_dir=[0,0,-1] (-Z), w_dir=[0,1,0] (Y)
# Origin at bbox_min_corner, so the rectangle is drawn at Z=0 and extruded in +Y

result = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(0, 0, 0))
    .rect(279.4, 50.8)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\108851_4d515b10_0007\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
