import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Wheel (bearing) - extruded annulus
# Outer radius: 132.5 mm, Inner radius: 75.0 mm, Extrude distance: 100.0 mm
# Frame: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
# This means the extrusion is along the X-axis (w_dir), sketch is on YZ plane

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\107668_cf76b132_0001\neg_01\iter_00\generated.step"

# Parameters from design plan
outer_radius = 132.5
inner_radius = 75.0
extrude_distance = 100.0

# Build on YZ plane (since w_dir = [1,0,0], sketch plane normal is X)
# The frame has u_dir=[0,0,-1], v_dir=[0,1,0], so sketch plane is YZ
# Center at origin

# Create the outer circle on YZ plane
result = (cq.Workplane("YZ")
    .circle(outer_radius)
    .extrude(extrude_distance))

# Cut the inner hole
inner = (cq.Workplane("YZ")
    .circle(inner_radius)
    .extrude(extrude_distance))

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
