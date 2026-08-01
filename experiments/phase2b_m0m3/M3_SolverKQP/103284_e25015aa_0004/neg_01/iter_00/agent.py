import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0004\neg_01\iter_00\generated.step"

# Design Plan parameters:
# - Circle center at (8.077681, 8.284339) in UV plane
# - Circle radius = 11.938 mm (from dimensions, scaled from 1.1938 cm)
# - Extrude distance = 12.7 mm (from dimensions, scaled from 1.27 cm)
# - Perturbation: extrude depth changed from 1.27 cm to 1.905 cm = 19.05 mm
#   BUT the design plan explicitly says 12.7 mm. We follow the design plan.

center_x = 8.077681
center_y = 8.284339
radius = 11.938
extrude_depth = 12.7  # mm, as per design plan

# Build the part: a simple disk (extruded circle)
result = (
    cq.Workplane("XY")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(extrude_depth)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
