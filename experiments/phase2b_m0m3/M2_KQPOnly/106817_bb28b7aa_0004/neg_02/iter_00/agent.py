import cadquery as cq
from cadquery import exporters
import math

# Design Plan: washer (extruded annulus)
# Dimensions (from design plan, in mm):
#   Outer radius: 5.5372
#   Inner radius: 1.9812
#   Extrude distance: 1.3208
#   Center (in sketch plane): (-25.400001, 12.7)
#   Normal direction: +w = (0, 1, 0)  (i.e., extrude along Y axis)
#   Workplane: XZ (since normal is Y, sketch plane is XZ)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0004\neg_02\iter_00/generated.step"

# Build the washer
# Start with a workplane on XZ (since normal is Y)
wp = cq.Workplane("XZ")

# Move to the center of the annulus
center_x = -25.400001
center_z = 12.7

# Outer circle
outer_radius = 5.5372
inner_radius = 1.9812
extrude_distance = 1.3208

# Create the outer circle and extrude
result = wp.moveTo(center_x, center_z).circle(outer_radius).extrude(extrude_distance)

# Cut the inner hole
# Create a cutting cylinder (inner circle extruded through)
cut_wp = cq.Workplane("XZ").moveTo(center_x, center_z).circle(inner_radius).extrude(extrude_distance * 1.5)
result = result.cut(cut_wp)

# Export
exporters.export(result, OUT_STEP_PATH)
