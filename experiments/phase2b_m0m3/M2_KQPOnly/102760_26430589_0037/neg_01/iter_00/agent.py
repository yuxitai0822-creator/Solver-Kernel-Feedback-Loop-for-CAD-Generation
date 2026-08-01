import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Disk: circle radius 0.8 mm, extrude 4.0 mm along w direction
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Extrude direction: -w (i.e., negative y direction)

# Build on XY plane, then rotate to match frame
# Start with circle on XY plane, extrude along Z, then rotate

# Create base workplane on XY
result = (cq.Workplane("XY")
          .circle(0.8)  # radius from design plan
          .extrude(4.0))  # extrude distance from design plan

# Now rotate to match the specified frame:
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the extrusion direction (w) should be [0,1,0]
# Currently extrusion is along +Z [0,0,1]
# We need to rotate so that Z maps to Y
# Rotation: X->X, Y->-Z, Z->Y
# This is a rotation of -90 degrees around X axis
result = result.rotate((0,0,0), (1,0,0), -90)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102760_26430589_0037\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)