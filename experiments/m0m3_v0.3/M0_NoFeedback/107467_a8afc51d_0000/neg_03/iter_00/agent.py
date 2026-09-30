import cadquery as cq
from cadquery import exporters
import math

# Design Plan: single disk (extruded circle)
# - Circle radius: 3.0 mm
# - Extrude distance: 14.0 mm along +Z
# - No inner holes (the previous script incorrectly added an inner loop)
# - Body count: 1
# - Surface type distribution: 1 CylinderSurfaceType + 2 PlaneSurfaceType

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107467_a8afc51d_0000\neg_03\iter_00/generated.step"

# Build the disk: circle radius 3.0, extrude 14.0 in +Z
result = (
    cq.Workplane("XY")
    .circle(3.0)          # radius 3.0 mm
    .extrude(14.0)        # extrude 14.0 mm along +Z
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
