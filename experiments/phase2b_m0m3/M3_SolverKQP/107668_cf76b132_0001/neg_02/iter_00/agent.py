import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Wheel (bearing) - extruded annulus
# Outer radius: 132.5 mm, Inner radius: 75.0 mm, Extrude distance: 100.0 mm
# Frame: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
# This means the extrusion direction is +w = +x axis
# The profile lies in the YZ plane (since w is x, u and v define YZ)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107668_cf76b132_0001\neg_02\iter_00/generated.step"

# Parameters from design plan
outer_radius = 132.5
inner_radius = 75.0
extrude_distance = 100.0

# Build the annulus on YZ plane (since extrusion is along X)
# Using Workplane("YZ") gives us the YZ plane as sketch plane
result = (
    cq.Workplane("YZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")