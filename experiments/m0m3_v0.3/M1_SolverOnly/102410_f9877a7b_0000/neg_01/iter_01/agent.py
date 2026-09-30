import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude depth = 11.5 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Workplane: XZ (since v_dir is [0,0,-1], normal is [0,1,0])

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102410_f9877a7b_0000\neg_01\iter_01/generated.step"

# Build the annulus on XZ plane (normal = Y axis)
wp = cq.Workplane("XZ")

# Create the outer circle and extrude it
result = wp.circle(6.0).extrude(11.5)

# Create the inner circle on the same workplane and extrude it for cutting
# Use the same workplane to ensure proper alignment
inner_wp = cq.Workplane("XZ")
cut = inner_wp.circle(4.25).extrude(11.5)

# Perform the cut operation
result = result.cut(cut)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
