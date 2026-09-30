import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0006\neg_03\iter_00\generated.step"

# Design Plan: rectangular frame (hollow box) with outer 500x300 mm, inner 400x200 mm, extruded 500 mm
# Perturbation: E4_void_remove - remove the inner void (make it solid)

# Outer rectangle dimensions (from design plan)
outer_u = 500.0  # length along u (x)
outer_v = 300.0  # width along v (y)
extrude_w = 500.0  # extrusion along w (z)

# Build the solid rectangular block (no inner void due to perturbation)
result = (
    cq.Workplane("XY")
    .rect(outer_u, outer_v)
    .extrude(extrude_w)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
