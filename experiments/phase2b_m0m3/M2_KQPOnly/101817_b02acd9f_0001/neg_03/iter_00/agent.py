import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0001\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 40x40 mm (centered at origin)
# Inner rectangle: 37.6x37.6 mm (centered at origin)
# Extrude distance: 520 mm in +Z direction

# Build the outer rectangle profile
outer = cq.Workplane("XY").rect(40.0, 40.0, centered=True)

# Build the inner rectangle profile (the hole)
inner = cq.Workplane("XY").rect(37.6, 37.6, centered=True)

# Create the base profile by subtracting inner from outer
# We need to combine them into a single wire
base_profile = outer.union(inner)

# Extrude the profile to create the hollow box
result = base_profile.extrude(520.0)

# Export the result
exporters.export(result, OUT_STEP_PATH)
