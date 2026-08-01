import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle
# Dimensions: length_u = 193.0 mm, width_v = 55.0 mm, extrude_distance = 50.0 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# The rectangle in UV space: (0,0) to (193,55) in UV, but note v_dir is [0,0,-1]
# so the rectangle lies in the XZ plane (u along X, v along -Z).
# Extrude along +w = +Y direction.

# Build the rectangle on the XZ plane
# Using Workplane("XZ") gives us X horizontal, Z vertical
# We want a rectangle from (0,0) to (193,55) in UV space
# U = X, V = -Z, so the rectangle corners in XYZ:
# (0,0,0), (193,0,0), (193,0,-55), (0,0,-55)
# But we can just use the Workplane rect method with centered=False

result = (
    cq.Workplane("XZ")
    .moveTo(0, 0)  # start at origin
    .rect(193.0, 55.0, centered=False)  # width=193 along X, height=55 along Z
    .extrude(50.0)  # extrude along +Y (normal of XZ plane)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双闭环反馈驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101427_a9bcb09c_0002\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)