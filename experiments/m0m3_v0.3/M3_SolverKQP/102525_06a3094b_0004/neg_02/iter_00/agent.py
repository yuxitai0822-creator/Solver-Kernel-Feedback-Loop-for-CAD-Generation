import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 8.5 x 18.0 x 2.5 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle centered at origin in uv-plane
# Extrude along +w (y-axis) by 2.5 mm

# Build the rectangle profile on XZ plane (since v_dir is -Z, u_dir is X)
# The rectangle spans u: [-4.25, 4.25], v: [-9.0, 9.0]
# In XZ coordinates: x from -4.25 to 4.25, z from -9.0 to 9.0

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)  # extrude along Y (positive direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0004\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)