import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Workplane: XZ (since v_dir is -Z, normal is Y)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102410_f9877a7b_0000\neg_01\iter_01/generated.step"

# Parameters from design plan (in mm)
outer_radius = 6.0
inner_radius = 4.25
extrude_distance = 11.5

# Build on XZ workplane (normal = Y axis)
wp = cq.Workplane("XZ")

# Create outer circle
outer = wp.center(0, 0).circle(outer_radius)

# Extrude the outer circle to create the base cylinder
result = outer.extrude(extrude_distance)

# Create inner hole by cutting with a cylinder
# Use the same workplane to create the inner circle and extrude it
inner = cq.Workplane("XZ").center(0, 0).circle(inner_radius).extrude(extrude_distance)
result = result.cut(inner)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
