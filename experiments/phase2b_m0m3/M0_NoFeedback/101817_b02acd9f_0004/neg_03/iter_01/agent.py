import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0004\neg_03\iter_01\generated.step"

# Design parameters from the design plan
# Rectangle dimensions: length_u = 1200.0 mm, width_v = 600.0 mm
# Extrude distance: 20.0 mm along w direction (which is [0,1,0] in world frame)
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# The profile coordinates in UV space are given, but we can just use the dimensions directly

# The profile rectangle in UV coordinates:
# start_uv: (127.82976131535646, -66.34402294937294) to (7.829761315356478, -66.34402294937294)
# This gives a width in U of 120.0 and height in V of 60.0
# But the dimensions say length_u=1200.0 and width_v=600.0
# The UV coordinates seem to be in cm (since compiler notes say cm_to_mm x10)
# So the actual rectangle in mm is 1200 x 600

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
# The rectangle center is at (127.82976131535646 + 7.829761315356478)/2 = 67.82976131535647 in U
# and (-66.34402294937294 + -6.344022949372942)/2 = -36.34402294937294 in V
# But we'll just use the dimensions directly for clarity

# Create the workplane on XZ (since v_dir is [0,0,-1], the sketch plane normal is w_dir=[0,1,0])
# So the sketch plane is XZ
result = (cq.Workplane("XZ")
    .center(67.82976131535647, -36.34402294937294)  # center of the rectangle in UV space
    .rect(120.0, 60.0)  # width=120 in U, height=60 in V (these are in cm, but we'll extrude 20mm)
    .extrude(20.0)  # extrude along w_dir=[0,1,0] by 20mm
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)