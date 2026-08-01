import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107668_cf76b132_0001\neg_02\iter_00\generated.step"

# Design Plan: Extruded annulus (wheel/bearing)
# Outer radius = 132.5 mm, Inner radius = 75.0 mm, Extrude distance = 100.0 mm
# Frame: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# This means the sketch plane is YZ (normal along X), and extrusion is along +X (w_dir)

# Build on YZ plane (normal = X axis)
result = (
    cq.Workplane("YZ")
    .circle(132.5)  # outer radius
    .circle(75.0)   # inner radius (creates a hole)
    .extrude(100.0) # extrude along X (positive direction)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
