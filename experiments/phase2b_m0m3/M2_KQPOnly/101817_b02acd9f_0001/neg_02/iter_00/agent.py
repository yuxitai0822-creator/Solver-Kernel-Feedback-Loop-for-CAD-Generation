import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0001\neg_02\iter_00/generated.step"

# Design Plan: rectangular frame, outer 40x40 mm, inner 37.6x37.6 mm, extrude 520 mm
# The outer rectangle spans from (-4,0) to (0,4) in UV space, but dimensions indicate 40x40 mm.
# The inner rectangle is offset by 0.12 mm from each edge, giving 37.6x37.6 mm.
# We'll construct the profile in the XY plane and extrude along Z.

# Create the outer rectangle centered at origin for simplicity
outer_rect = cq.Workplane("XY").rect(40.0, 40.0, centered=True)

# Create the inner rectangle (the hole)
inner_rect = cq.Workplane("XY").rect(37.6, 37.6, centered=True)

# Build the profile: outer rectangle with inner rectangle subtracted
# We need to create a wire from the outer rect, then cut the inner rect
profile = outer_rect.rect(40.0, 40.0, centered=True).extrude(0.1)  # dummy extrude to get a face

# Better approach: use the workplane to create the profile directly
# Start with the outer rectangle as a closed wire
result = cq.Workplane("XY").rect(40.0, 40.0, centered=True).extrude(520.0)

# Now cut the inner hole
inner_cut = cq.Workplane("XY").rect(37.6, 37.6, centered=True).extrude(520.0)
result = result.cut(inner_cut)

# Export
cq.exporters.export(result, OUT_STEP_PATH)