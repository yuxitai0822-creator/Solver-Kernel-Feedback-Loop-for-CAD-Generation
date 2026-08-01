import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 132.5 mm, inner radius = 75.0 mm, extrude distance = 100.0 mm
# Frame: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# This means the extrusion direction is +w = +x axis
# The profile lies in the YZ plane (since u and v span YZ)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107668_cf76b132_0001\neg_01\iter_01/generated.step"

# Build the annulus profile on the YZ plane (workplane='YZ')
# The center is at (0,0) in UV coordinates, which maps to YZ plane origin
outer_radius = 132.5
inner_radius = 75.0
extrude_distance = 100.0

# Create workplane on YZ plane
wp = cq.Workplane("YZ")

# Create outer circle
outer = wp.moveTo(0, 0).circle(outer_radius)

# Create inner circle (for cutting)
inner = wp.moveTo(0, 0).circle(inner_radius)

# Extrude the outer circle along +X direction (which is +w in the frame)
result = outer.extrude(extrude_distance)

# Cut the inner hole by extruding the inner circle and subtracting
inner_prism = inner.extrude(extrude_distance)
result = result.cut(inner_prism)

# Export
cq.exporters.export(result, OUT_STEP_PATH)