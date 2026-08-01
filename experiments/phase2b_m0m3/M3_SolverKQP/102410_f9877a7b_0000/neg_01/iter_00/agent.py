import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102410_f9877a7b_0000\neg_01\iter_00\generated.step"

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Workplane: XZ (since v_dir is -Z, w_dir is Y, so sketch on XZ plane)

# Build the outer circle
result = (
    cq.Workplane("XZ")
    .circle(6.0)  # outer radius
    .extrude(11.5)  # extrude along Y (w_dir)
)

# Cut the inner hole
inner = (
    cq.Workplane("XZ")
    .circle(4.25)
    .extrude(11.5)
)

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
