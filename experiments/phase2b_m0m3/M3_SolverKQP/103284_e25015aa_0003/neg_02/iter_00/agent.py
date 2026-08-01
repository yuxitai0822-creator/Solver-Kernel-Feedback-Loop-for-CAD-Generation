import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0003\neg_02\iter_00/generated.step"

# Design Plan parameters:
# - Circle center: (16.994660913961006, 17.998556732836484)
# - Circle radius: 25.4 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 8.89 mm (from dimensions.extrude_distance)
# - The perturbed radius in the previous script was 31.75 (incorrectly scaled)
# - The correct radius is 25.4 mm (as per design plan)

# Build the part
result = (
    cq.Workplane("XY")
    .moveTo(16.994660913961006, 17.998556732836484)
    .circle(25.4)  # radius in mm
    .extrude(8.89)  # extrude distance in mm
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
