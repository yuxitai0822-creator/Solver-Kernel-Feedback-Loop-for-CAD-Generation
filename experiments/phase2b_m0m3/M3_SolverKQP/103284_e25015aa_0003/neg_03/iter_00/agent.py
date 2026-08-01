import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103284_e25015aa_0003\neg_03\iter_00/generated.step"

# Design Plan: single disk (extruded circle)
# - Circle radius: 25.4 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 8.89 mm (from dimensions.extrude_distance)
# - Center: (16.994661, 17.998557) in UV plane
# - No inner holes (the previous script had an erroneous inner loop with radius 0.5)
# - Body count: 1
# - Surface types: 1 CylindricalSurface (outer wall) + 2 PlanarSurface (top/bottom)

# Build the workplane and create the disk
result = (
    cq.Workplane("XY")
    .moveTo(16.994661, 17.998557)
    .circle(25.4)
    .extrude(8.89)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
