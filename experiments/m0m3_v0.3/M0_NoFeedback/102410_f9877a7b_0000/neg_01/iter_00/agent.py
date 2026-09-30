import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Workplane: XZ (since v_dir is -Z, normal is Y)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102410_f9877a7b_0000\neg_01\iter_00/generated.step"

# Parameters from design plan (in mm)
outer_radius = 6.0
inner_radius = 4.25
extrude_distance = 11.5

# Build on XZ workplane (normal = Y axis)
wp = cq.Workplane("XZ")

# Create outer circle
outer = wp.center(0, 0).circle(outer_radius)

# Create inner circle (hole)
inner = wp.center(0, 0).circle(inner_radius)

# Extrude the outer circle
result = outer.extrude(extrude_distance)

# Cut the inner hole
# Create a cutting cylinder that extends through the body
cut_cylinder = inner.extrude(extrude_distance * 1.5)
result = result.cut(cut_cylinder)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
