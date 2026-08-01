import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0001\neg_02\iter_00/generated.step"

# Design Plan: horizontal leg 1
# Extruded rectangular frame (hollow box)
# Outer profile: 40x40 mm square (centered at origin)
# Inner profile: 37.6x37.6 mm square (centered at origin)
# Extrude distance: 520 mm in +Z direction
# No inner loops (perturbation: void removed)

# Build the outer rectangle (40x40 mm)
outer = cq.Workplane("XY").rect(40.0, 40.0, centered=True).extrude(520.0)

# Build the inner rectangle (37.6x37.6 mm) for the hollow cutout
inner = cq.Workplane("XY").rect(37.6, 37.6, centered=True).extrude(520.0)

# Subtract inner from outer to create the hollow frame
result = outer.cut(inner)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
