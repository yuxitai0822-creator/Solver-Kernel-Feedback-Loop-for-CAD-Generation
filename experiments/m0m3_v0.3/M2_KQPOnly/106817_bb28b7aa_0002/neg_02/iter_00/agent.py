import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Profile: circle with radius 4.87045 mm (from dimensions.profiles[0].radius)
# Extrude distance: 6.8707 mm (from dimensions.extrude_distance)
# The circle center in UV is (114.300004, 0.0) but that's in the frame's UV space.
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the sketch plane is XZ (u=x, v=-z), extrude along +w = +y

# Build the part
result = (
    cq.Workplane("XZ")  # sketch plane: u=x, v=-z
    .circle(4.87045)     # radius from design plan
    .extrude(6.8707)     # extrude along +y (w direction)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0002\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)