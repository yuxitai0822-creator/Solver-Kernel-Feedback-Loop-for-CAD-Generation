import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0001\neg_02\iter_00/generated.step"

# Design Plan: horizontal leg 1
# Extruded rectangular frame with outer 40x40 mm and inner 37.6x37.6 mm, extruded 520 mm
# Perturbation: E4_void_remove - remove the inner void (make solid bar)

# Outer rectangle dimensions (in mm, from design plan)
outer_length_u = 40.0  # along x
outer_width_v = 40.0   # along y
extrude_distance = 520.0  # along z

# Build the solid bar (no inner void due to perturbation)
result = (
    cq.Workplane("XY")
    .rect(outer_length_u, outer_width_v, centered=True)
    .extrude(extrude_distance)
)

# Export
importers = cq.exporters
exporters.export(result, OUT_STEP_PATH)
