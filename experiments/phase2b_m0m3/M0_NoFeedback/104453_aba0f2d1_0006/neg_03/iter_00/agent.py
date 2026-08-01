import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\104453_aba0f2d1_0006\neg_03\iter_00\generated.step"

# Design Plan: rectangular frame (hollow box) with outer 500x300 mm, inner 400x200 mm, extruded 500 mm
# The perturbation is E4_void_remove: we remove the inner void, making it a solid rectangular prism.

# Outer rectangle dimensions (from design plan profiles)
outer_u = 500.0  # length along u (x)
outer_v = 300.0  # width along v (y)
extrude_distance = 500.0  # along w (z)

# Build the solid rectangular prism (no inner hole)
result = (
    cq.Workplane("XY")
    .rect(outer_u, outer_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
