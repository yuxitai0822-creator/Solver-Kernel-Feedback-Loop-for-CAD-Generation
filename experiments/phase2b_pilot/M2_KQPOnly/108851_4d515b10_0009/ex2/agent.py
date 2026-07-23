import cadquery as cq

# Build an extruded rectangle (flat plate/panel)
# Profile: rectangle 20.955 mm (u) x 5.7912 mm (v)
# Extrude: 19.05 mm along +w direction
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
# Origin convention: bbox_min_corner

result = (
    cq.Workplane("XZ")
    .transformed(offset=(0, 0, 0), rotate=(0, 0, 0))
    .rect(20.955, 5.7912)
    .extrude(19.05)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\108851_4d515b10_0009\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
