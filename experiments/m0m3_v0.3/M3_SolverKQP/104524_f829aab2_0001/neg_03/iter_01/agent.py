import cadquery as cq

# Design Plan: screw (disk) with radius 7.5 mm, extrude 20.0 mm
# Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# Circle in UV plane (XZ plane in world), extrude along +w (Y axis)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104524_f829aab2_0001\neg_03\iter_01/generated.step"

# Build the disk: circle radius 7.5 mm, extrude 20.0 mm along Y
# Using XZ workplane (normal = Y), circle centered at origin
result = (
    cq.Workplane("XZ")
    .circle(7.5)
    .extrude(20.0)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)