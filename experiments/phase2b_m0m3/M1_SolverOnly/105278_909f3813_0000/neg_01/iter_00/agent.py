import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\105278_909f3813_0000\neg_01\iter_00\generated.step"

# Design Plan dimensions (in mm):
# Rectangle: length_u = 12.0 mm (along x), width_v = 60.0 mm (along z)
# Extrude: distance_total = 40.0 mm (along y, +w direction)
# Frame: u_dir = [1,0,0] (x), v_dir = [0,0,-1] (negative z), w_dir = [0,1,0] (y)
# The profile is defined in UV space, where u corresponds to x, v corresponds to z (but inverted)
# The rectangle in UV: u from -0.6 to 0.6, v from -3.0 to 3.0
# After scaling: u range = 1.2, v range = 6.0
# But the dimensions say length_u = 12.0, width_v = 60.0, so scaling factor is 10x
# So the rectangle in mm: u from -6.0 to 6.0, v from -30.0 to 30.0

# Build the part using CadQuery
result = (
    cq.Workplane("XZ")  # Sketch on XZ plane (u=x, v=z)
    .center(0, 0)  # Center at origin
    .rect(12.0, 60.0)  # Rectangle: 12mm along x, 60mm along z
    .extrude(40.0)  # Extrude 40mm along y (positive y direction)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
