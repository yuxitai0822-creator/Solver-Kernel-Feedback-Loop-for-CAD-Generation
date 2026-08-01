import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Disk: extruded circle
# Radius = 25.4 mm (from dimensions.profiles[0].radius.value)
# Extrude distance = 8.89 mm (from dimensions.extrude_distance.value)
# Center in UV plane: (16.994661, 17.998557) - but we center at origin for simplicity
# since the design plan doesn't specify absolute position constraints

# Build the disk
result = (
    cq.Workplane("XY")
    .circle(25.4)  # radius in mm
    .extrude(8.89)  # extrude distance in mm
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\103284_e25015aa_0003\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)