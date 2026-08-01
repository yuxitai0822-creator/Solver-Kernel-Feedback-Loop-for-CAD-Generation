import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
OUTER_RADIUS = 6.0  # mm (original 0.6 cm * 10 = 6.0 mm)
INNER_RADIUS = 4.25  # mm (original 0.425 cm * 10 = 4.25 mm)
HEIGHT = 12.0  # mm (original 1.2 cm * 10 = 12.0 mm)

# Build the part
# Start with a workplane on the XZ plane (as per the original script's WORKPLANE = 'XZ')
# But the design plan's frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the extrusion direction is +w = +y, so we should work on the XZ plane
result = (
    cq.Workplane("XZ")
    .circle(OUTER_RADIUS)
    .circle(INNER_RADIUS)
    .extrude(HEIGHT)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102410_f9877a7b_0012\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)