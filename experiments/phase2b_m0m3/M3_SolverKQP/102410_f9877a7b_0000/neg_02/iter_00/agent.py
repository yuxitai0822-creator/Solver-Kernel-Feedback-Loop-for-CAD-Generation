import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102410_f9877a7b_0000\neg_02\iter_00\generated.step"

# Design Plan: extruded annulus
# Outer radius = 6.0 mm (from dimensions, not the perturbed 7.5)
# Inner radius = 4.25 mm
# Extrude distance = 11.5 mm
# Workplane: XZ (as in original script, but we'll use XY for simplicity and correct orientation)
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the sketch plane is XY (u,v) and extrude along w = Y direction

# Build the annulus profile on XY plane, extrude along Y axis
result = (
    cq.Workplane("XY")
    .circle(6.0)  # outer radius = 6.0 mm (from design plan dimensions, not perturbed)
    .circle(4.25)  # inner radius = 4.25 mm
    .extrude(11.5)  # extrude distance = 11.5 mm along +Z (but we need along Y)
)

# The above extrudes along Z, but we need along Y. Let's rotate the result.
# Actually, simpler: use workplane XZ and extrude along Y.
# Let's redo properly:
result = (
    cq.Workplane("XZ")
    .circle(6.0)
    .circle(4.25)
    .extrude(11.5)  # extrudes along Y axis
)

exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")