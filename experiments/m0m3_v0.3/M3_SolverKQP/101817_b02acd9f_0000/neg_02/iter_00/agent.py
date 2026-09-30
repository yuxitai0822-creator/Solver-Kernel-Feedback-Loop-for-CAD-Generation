import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0000\neg_02\iter_00/generated.step"

# Design Plan: rectangular frame (hollow box) with outer 40x40 mm, inner 37.6x37.6 mm, extruded 780 mm along Y
# The frame is defined in UV space where U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# Outer rectangle: from (6,-7) to (10,-3) in UV -> width=4, height=4 -> scaled by 10? 
# Actually the coordinates are in cm originally (converted to mm by x10). 
# Outer: start_uv (10,-7) to (6,-7) etc. In mm: (100,-70) to (60,-70) etc.
# The outer rectangle spans from u=6 to u=10 (width=4) and v=-7 to v=-3 (height=4).
# After cm->mm conversion: width=40mm, height=40mm.
# Inner rectangle: from (6.12,-6.88) to (9.88,-3.12) -> width=3.76, height=3.76 -> 37.6mm x 37.6mm

# Build on XZ plane (since V is [0,0,-1] which is Z, U is X, W is Y)
# The sketch is on XZ plane, extrude along Y

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(40, 40, centered=True)  # outer rectangle, centered at origin
    .extrude(780.0)
)

# Cut inner hole
inner = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(37.6, 37.6, centered=True)
    .extrude(780.0)
)

result = result.cut(inner)

exporters.export(result, OUT_STEP_PATH)
