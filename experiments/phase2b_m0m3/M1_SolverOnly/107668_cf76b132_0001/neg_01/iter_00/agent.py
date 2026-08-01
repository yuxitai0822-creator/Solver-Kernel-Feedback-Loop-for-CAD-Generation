import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Wheel (bearing) - extruded annulus
# Outer radius: 132.5 mm, Inner radius: 75.0 mm, Extrude distance: 100.0 mm
# Frame: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
# This means the sketch is on the YZ plane, extruded along X axis

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107668_cf76b132_0001\neg_01\iter_00/generated.step"

# Parameters from design plan
outer_radius = 132.5
inner_radius = 75.0
extrude_distance = 100.0

# Create workplane on YZ plane (since w_dir = [1,0,0], sketch is on YZ)
# The frame has u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
# So the sketch plane normal is w_dir = [1,0,0], meaning YZ plane
# u corresponds to -Z, v corresponds to Y

# Build the annulus on YZ plane
result = (
    cq.Workplane("YZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
