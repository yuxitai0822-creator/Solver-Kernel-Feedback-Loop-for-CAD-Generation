import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0001\neg_01\iter_00\generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion x10):
# Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
# Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
# Extrude distance: 25.0 mm (original was 2.5 cm = 25 mm, perturbed to 3.75 cm = 37.5 mm)
# Per the perturbation description: operator=E2_extrude_depth; original=2.5; perturbed=3.75
# So we use 37.5 mm as the extrude depth.

EXTENT_TOTAL_MM = 37.5  # Perturbed value: 3.75 cm = 37.5 mm

# Build the outer rectangle
outer = cq.Workplane("XZ").moveTo(96.5, 27.5).rect(198.0, 60.0, centered=True)

# Build the inner rectangle for the hole
inner = cq.Workplane("XZ").moveTo(96.5, 27.5).rect(193.0, 55.0, centered=True)

# Extrude the outer rectangle
result = outer.extrude(EXTENT_TOTAL_MM)

# Cut the inner hole
cut_prism = inner.extrude(EXTENT_TOTAL_MM * 1.5)
result = result.cut(cut_prism)

exporters.export(result, OUT_STEP_PATH)
