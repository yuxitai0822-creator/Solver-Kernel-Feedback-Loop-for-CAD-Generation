import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk) with radius 7.5 mm and extrude distance 20.0 mm
# The frame has w_dir = [0,1,0] (extrude direction is +w = +Y)
# Workplane is XZ (normal = Y) to match the frame's w_dir

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104524_f829aab2_0001\neg_01\iter_00/generated.step"

# Parameters from design plan
radius = 7.5  # mm (from profiles[0].radius.value)
extrude_distance = 20.0  # mm (from extrude.distance_total.value)

# Build the disk: circle on XZ plane, extrude along Y axis
result = (
    cq.Workplane("XZ")
    .circle(radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
