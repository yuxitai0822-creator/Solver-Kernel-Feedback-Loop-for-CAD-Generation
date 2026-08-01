import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104283_e5646f96_0000\neg_03\iter_00/generated.step"

# Design Plan: extruded circle (disk)
# Profile: circle centered at (-15.0, 10.0) with radius 12.5 mm
# Extrude: 75.0 mm along +w direction (which maps to +X in world frame)
# The frame has u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# So the sketch plane is YZ (normal = u_dir cross v_dir = (1,0,0) = w_dir)
# We work on YZ plane, extrude along X

# Build the circle on YZ plane
result = (
    cq.Workplane("YZ")
    .moveTo(-15.0, 10.0)  # center in YZ coordinates
    .circle(12.5)          # radius
    .extrude(75.0)         # extrude along X (positive direction)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
