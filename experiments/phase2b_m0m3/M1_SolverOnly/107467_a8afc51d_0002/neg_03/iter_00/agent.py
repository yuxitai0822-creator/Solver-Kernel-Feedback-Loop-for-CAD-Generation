import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107467_a8afc51d_0002\neg_03\iter_00\generated.step"

# Design Plan: extruded circle (disk)
# - Circle radius: 3.0 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 25.0 mm (from dimensions.extrude_distance)
# - No inner holes (only outer ring, no inner loops in design plan)
# - Body count: 1

# Build the disk
result = (
    cq.Workplane("XY")
    .circle(3.0)          # radius 3.0 mm
    .extrude(25.0)        # extrude 25.0 mm in +Z
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
