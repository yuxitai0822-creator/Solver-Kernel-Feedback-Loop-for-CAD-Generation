import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107467_a8afc51d_0002\neg_02\iter_00\generated.step"

# Design parameters from the plan:
# - Circle radius: 3.0 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 25.0 mm (from dimensions.extrude_distance)
# - The profile circle radius in the curves is 0.3 (normalized), but the actual dimension is 3.0 mm
# - The perturbation changed the curve radius to 0.375, but the actual dimension should remain 3.0 mm

# Build the disk: extrude a circle of radius 3.0 mm by 25.0 mm
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius in mm
    .extrude(25.0)  # height in mm
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
