import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0006\neg_01\iter_00\generated.step"

# Design Plan: rectangular prism, extruded rectangle
# Dimensions: length_u=11.3 mm, width_v=21.0 mm, extrude_distance=3.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in UV plane
# UV coordinates: u from -0.565 to 0.565, v from -1.05 to 1.05
# After scaling: u spans 11.3 mm, v spans 21.0 mm
# Extrude in +w direction (y-axis) by 3.0 mm

# Build on XY plane, then rotate to match frame orientation
# Frame: u=x, v=-z, w=y
# So we sketch on XZ plane (u,v) and extrude along Y (w)

# Create workplane on XZ
wp = cq.Workplane("XZ")

# Rectangle centered at origin, dimensions: 11.3 (u/x) x 21.0 (v/z)
# Note: v_dir is [0,0,-1], so positive v in UV maps to negative Z
# But rectangle is symmetric, so centered works fine
result = wp.center(0, 0).rect(11.3, 21.0).extrude(3.0)

# Export
exporters.export(result, OUT_STEP_PATH)
