import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 12mm x 60mm x 40mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Rectangle in UV plane: u from -0.6 to 0.6, v from -3.0 to 3.0
# Extrude along +w by 40.0 mm

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1], u_dir is [1,0,0])
# The rectangle center is at (0, 0) in UV, which maps to (0, 0) in XZ
# Width along u = 1.2 mm, height along v = 6.0 mm
# But the design plan says length_u=12.0, width_v=60.0 - these are the actual dimensions
# The UV coordinates are -0.6 to 0.6 (span 1.2) and -3.0 to 3.0 (span 6.0)
# This is a scaling factor of 10x from the UV coordinates to actual dimensions
# So the rectangle is 12mm x 60mm

# Create workplane on XZ (since v_dir is [0,0,-1], the sketch plane is XZ)
# The rectangle center is at (0, 0) in the sketch plane
result = (cq.Workplane("XZ")
    .center(0, 0)
    .rect(12.0, 60.0, centered=True)
    .extrude(40.0)  # extrude along +Y (which is +w direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\105278_909f3813_0000\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)