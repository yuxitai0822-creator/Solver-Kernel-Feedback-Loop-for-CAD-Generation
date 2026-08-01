import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Disk: extruded circle
# Radius = 25.4 mm (from dimensions.profiles[0].radius.value)
# Extrude distance = 8.89 mm (from dimensions.extrude_distance.value)
# Center in UV: (16.994661, 17.998557) - but we'll center at origin for simplicity
# The design plan specifies a simple disk (cylinder)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\103284_e25015aa_0003\neg_02\iter_00/generated.step"

# Build the disk
# Using the dimensions from the design plan:
# radius = 25.4 mm (from dimensions.profiles[0].radius.value)
# extrude distance = 8.89 mm (from dimensions.extrude_distance.value)

radius = 25.4  # mm
height = 8.89  # mm

# Create the disk centered at origin
result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(height)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
