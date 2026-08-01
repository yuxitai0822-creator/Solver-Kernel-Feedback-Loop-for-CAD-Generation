import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle plate
# Dimensions: length_u=1200.0 mm, width_v=600.0 mm, extrude_distance=20.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from 7.83 to 127.83, v from -66.34 to -6.34
# Note: The design plan coordinates are in mm (converted from cm)

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1] and w_dir is [0,1,0])
# The rectangle in UV coordinates maps to XZ plane: u -> x, v -> z
# Center the rectangle for simplicity, matching the design plan extents

# Rectangle dimensions from design plan
length_u = 1200.0  # mm
width_v = 600.0    # mm
extrude_distance = 20.0  # mm

# Create workplane on XZ plane
wp = cq.Workplane("XZ")

# Draw rectangle centered at origin
# The rectangle spans: u from 7.83 to 127.83 (width 120.0? No, that's 120.0)
# Wait, the design plan says length_u=1200.0, width_v=600.0
# But the profile coordinates show u range: 7.83 to 127.83 (width 120.0)
# and v range: -66.34 to -6.34 (height 60.0)
# This is a 10x scale difference - the profile was in cm, dimensions in mm
# The design plan explicitly states dimensions: length_u=1200.0, width_v=600.0, extrude=20.0
# So we use the explicit dimensions from the design plan

# Build the rectangle
result = wp.rect(length_u, width_v).extrude(extrude_distance)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0004\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
