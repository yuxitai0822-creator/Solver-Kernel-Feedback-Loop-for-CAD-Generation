import cadquery as cq
from cadquery import exporters
import math

# Design Plan: single disk (extruded circle)
# - Circle radius = 3.0 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance = 25.0 mm (from dimensions.extrude_distance.value)
# - No inner holes (only one outer ring, no inner loops)
# - Body count = 1
# - Span u = 6.0, span v = 6.0, span w = 25.0
# - Surface types: 1 CylinderSurfaceType, 2 PlaneSurfaceType

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107467_a8afc51d_0002\neg_03\iter_00\generated.step"

# Build the disk: circle radius 3.0, extrude 25.0 mm in +Z
result = (
    cq.Workplane("XY")
    .circle(3.0)          # radius = 3.0 mm
    .extrude(25.0)        # extrude 25.0 mm in +Z direction
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
