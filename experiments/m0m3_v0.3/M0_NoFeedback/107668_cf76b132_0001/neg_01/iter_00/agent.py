import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107668_cf76b132_0001\neg_01\iter_00\generated.step"

# Design Plan parameters (all in mm, unit conversion already applied)
OUTER_RADIUS = 132.5  # from dimensions.outer_radius
INNER_RADIUS = 75.0   # from dimensions.inner_radius
EXTRUDE_DISTANCE = 100.0  # from dimensions.extrude_distance (perturbed value)

# Build the annulus on the YZ plane (as per the frame: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0])
# The sketch plane is YZ (normal along X), which matches w_dir = [1,0,0]
result = (
    cq.Workplane("YZ")
    .center(0, 0)
    .circle(OUTER_RADIUS)
    .circle(INNER_RADIUS)
    .extrude(EXTRUDE_DISTANCE)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
