import cadquery as cq
import math
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104453_aba0f2d1_0002\neg_01\iter_01\generated.step"

# Build the stadium profile as per design plan:
# Dimensions: straight_length=500 mm, radius=50 mm, extrude=100 mm
# Overall span in u (x): 600 mm (500 + 2*50)
# Overall span in v (y): 100 mm (2*50)

wp = cq.Workplane("XY")

N_ARC = 64  # number of segments per arc

# Build profile starting at top-left of left arc: (0, 50)
wp = wp.moveTo(0, 50)

# Top line from (0,50) to (500,50)
wp = wp.lineTo(500, 50)

# Right arc: center (500,0), radius 50, from angle 90° to -90° (clockwise top to bottom)
for i in range(1, N_ARC + 1):
    t = math.pi/2 - math.pi * i / N_ARC  # from 90° down to -90°
    x = 500 + 50 * math.cos(t)
    y = 50 * math.sin(t)
    wp = wp.lineTo(x, y)

# Bottom line from (500,-50) to (0,-50)
wp = wp.lineTo(0, -50)

# Left arc: center (0,0), radius 50, from angle -90° to 90° (bottom to top)
for i in range(1, N_ARC + 1):
    t = -math.pi/2 + math.pi * i / N_ARC  # from -90° up to 90°
    x = 50 * math.cos(t)
    y = 50 * math.sin(t)
    wp = wp.lineTo(x, y)

wp = wp.close()

# Extrude 100 mm in +z direction
result = wp.extrude(100.0)

exporters.export(result, OUT_STEP_PATH)