import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 8.5 x 18.0 x 2.5 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in uv-plane
# Extrude along +w (y-axis) by 2.5 mm

# Build the rectangle profile on the XZ plane (since v_dir is [0,0,-1], u is X, v is Z)
# The rectangle spans u: [-4.25, 4.25] and v: [-9.0, 9.0] (since width_v=18.0)
# But the profile curves show start_uv: (0.425, -0.9) etc. which are in cm? 
# Actually the design plan says unit is mm, and dimensions are 8.5 x 18.0 x 2.5 mm
# The profile coordinates in the plan are in cm (0.425 cm = 4.25 mm, 0.9 cm = 9.0 mm)
# So we use mm directly: rectangle from (-4.25, -9.0) to (4.25, 9.0)

# Create workplane on XZ (since v_dir is [0,0,-1], the sketch plane is XZ)
# But we need to orient correctly: u_dir=[1,0,0] (X), v_dir=[0,0,-1] (negative Z)
# So the sketch plane normal is w_dir = [0,1,0] (Y)
# We'll use cq.Workplane("XZ") which has normal Y, then adjust

wp = cq.Workplane("XZ")

# Draw rectangle centered at origin
wp = wp.moveTo(0, 0).rect(8.5, 18.0, centered=True)

# Extrude along +w direction which is [0,1,0] (positive Y)
# Since Workplane("XZ") extrudes along Y by default
result = wp.extrude(2.5)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0004\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
