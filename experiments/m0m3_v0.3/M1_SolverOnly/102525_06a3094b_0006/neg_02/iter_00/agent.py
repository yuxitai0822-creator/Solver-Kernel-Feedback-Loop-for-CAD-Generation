import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102525_06a3094b_0006\neg_02\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 11.3 x 21.0 x 3.0 mm
# The profile is a rectangle centered at origin in the XZ plane
# Extrude along Y axis (positive direction) by 3.0 mm

# Create workplane on XZ plane (Y normal)
wp = cq.Workplane("XZ")

# Rectangle dimensions from design plan
length_u = 11.3  # along X axis
width_v = 21.0   # along Z axis (since v_dir is [0,0,-1], but magnitude is 21.0)
extrude_distance = 3.0  # along Y axis (w_dir is [0,1,0])

# Build rectangle centered at origin
result = wp.center(0, 0).rect(length_u, width_v).extrude(extrude_distance)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
