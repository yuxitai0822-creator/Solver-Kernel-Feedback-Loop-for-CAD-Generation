import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0000\neg_03\iter_01/generated.step"

# Design Plan: rectangular frame (hollow box) with outer 40x40 mm, inner 37.6x37.6 mm, extruded 780 mm
# The perturbation (E4_void_remove) removes the inner void, so we produce a solid rectangular prism.
# Outer rectangle: from (6.0, -7.0) to (10.0, -3.0) in UV space, but scaled by 10 (cm->mm conversion).
# Actually the design plan says outer_length_u=40.0, outer_width_v=40.0, inner_length_u=37.6, inner_width_v=37.6.
# The UV coordinates in the plan are: outer: (10,-7) to (6,-7) etc. These are in cm? The compiler notes say cm_to_mm (x10).
# So the actual mm coordinates: outer rectangle from (60, -70) to (100, -30) in mm? Let's check: 10cm=100mm, 6cm=60mm, 7cm=70mm, 3cm=30mm.
# So outer: x from 60 to 100 (width 40mm), y from -70 to -30 (height 40mm). Inner: x from 61.2 to 98.8 (width 37.6mm), y from -68.8 to -31.2 (height 37.6mm).
# Since perturbation removes the void, we only create the outer rectangle and extrude.

# Build the outer rectangle on XZ plane (as per previous script's WORKPLANE='XZ')
wp = cq.Workplane("XZ")

# Outer rectangle centered at (80, -50) with width 40, height 40
result = wp.moveTo(80, -50).rect(40, 40, centered=True).extrude(780.0)

exporters.export(result, OUT_STEP_PATH)