import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\105278_909f3813_0000\neg_01\iter_00/generated.step"

# Design Plan: rectangular prism 12mm x 60mm x 40mm
# The profile is a rectangle in the UV plane, where:
#   u_dir = [1,0,0] (X axis)
#   v_dir = [0,0,-1] (negative Z axis)
#   w_dir = [0,1,0] (Y axis) - extrusion direction
#
# Profile dimensions from design plan:
#   length_u = 12.0 mm (span along u_dir = X axis)
#   width_v = 60.0 mm (span along v_dir = -Z axis)
# Extrude distance = 40.0 mm along +w_dir = +Y axis
#
# The profile curves define a rectangle centered at (0,0) in UV space:
#   u range: [-0.6, 0.6]  (total 1.2 in UV space, but actual length is 12mm)
#   v range: [-3.0, 3.0]  (total 6.0 in UV space, but actual width is 60mm)
# The scaling factor from UV to mm is 10x (since 1.2 -> 12mm and 6.0 -> 60mm)
#
# We'll build this directly using cadquery primitives.

# Build the rectangle on the XZ plane (since v_dir = -Z, u_dir = X)
# The rectangle center is at (0, 0) in the XZ plane
# Width along X = 12.0 mm, height along Z = 60.0 mm
result = (cq.Workplane("XZ")
          .center(0, 0)
          .rect(12.0, 60.0, centered=True)
          .extrude(40.0))  # extrude along Y axis (positive direction)

exporters.export(result, OUT_STEP_PATH)
