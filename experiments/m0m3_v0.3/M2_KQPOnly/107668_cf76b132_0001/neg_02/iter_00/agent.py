import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Wheel (bearing) - extruded annulus
# Outer radius = 132.5 mm, Inner radius = 75.0 mm, Extrude distance = 100.0 mm
# Extrusion direction: +w = [1, 0, 0] (X-axis)
# Workplane: YZ (since normal is X-axis)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\107668_cf76b132_0001\neg_02\iter_00/generated.step"

# Parameters from design plan
outer_radius = 132.5  # mm
inner_radius = 75.0   # mm
extrude_distance = 100.0  # mm

# Build the annulus on YZ plane (normal = X-axis)
# Start with outer circle, then cut inner circle
result = (
    cq.Workplane("YZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
