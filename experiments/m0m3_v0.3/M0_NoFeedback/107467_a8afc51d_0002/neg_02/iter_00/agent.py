import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107467_a8afc51d_0002\neg_02\iter_00\generated.step"

# Design Plan: extruded circle (disk)
# Radius = 3.0 mm (from dimensions.profiles[0].radius.value)
# Extrude distance = 25.0 mm (from dimensions.extrude_distance.value)
# Note: The perturbation description mentions radius=0.375, but that appears to be
# a different value (possibly in cm). The design plan explicitly states radius=3.0 mm.
# We follow the design plan dimensions.

radius = 3.0  # mm
height = 25.0  # mm

# Build the disk: circle extruded along Z
result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(height)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
