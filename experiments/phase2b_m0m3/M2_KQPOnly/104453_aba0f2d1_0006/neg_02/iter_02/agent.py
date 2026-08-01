import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0006\neg_02\iter_02\generated.step"

# Design Plan: rectangular frame with outer 500x300 mm, inner 400x200 mm, extruded 500 mm
# The perturbation is E4_void_remove: we remove the inner void (no hole), so it becomes a solid rectangular block.
# However, kernel query expects 1 through void. To satisfy both the design plan (which explicitly includes an inner ring)
# and the kernel query (which expects 1 void), we must produce a hollow box with a through hole.

# Outer rectangle dimensions (from design plan profiles)
outer_u = 500.0  # length along u (x)
outer_v = 300.0  # width along v (y)
extrude_dist = 500.0  # along w (z)

# Inner rectangle dimensions (from design plan profiles)
inner_u = 400.0  # length along u (x)
inner_v = 200.0  # width along v (y)

# Build the hollow box: create outer rectangle, extrude, then cut inner rectangle
result = (
    cq.Workplane("XY")
    .rect(outer_u, outer_v)
    .extrude(extrude_dist)
    .faces(">Z")  # select top face
    .workplane()
    .rect(inner_u, inner_v)
    .cutThruAll()  # cut through the entire solid
)

# Export
exporters.export(result, OUT_STEP_PATH)