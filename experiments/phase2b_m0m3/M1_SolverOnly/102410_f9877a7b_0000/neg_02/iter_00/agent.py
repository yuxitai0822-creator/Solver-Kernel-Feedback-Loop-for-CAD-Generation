import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102410_f9877a7b_0000\neg_02\iter_00\generated.step"

# Design parameters from the design plan (unit: mm)
outer_radius = 6.0  # from dimensions.outer_radius (value 6.0)
inner_radius = 4.25  # from dimensions.inner_radius (value 4.25)
extrude_distance = 11.5  # from dimensions.extrude_distance (value 11.5)

# Build the annulus profile on the XZ plane (as per the original script's WORKPLANE = 'XZ')
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the sketch plane is XZ (u along X, v along -Z, normal along Y)
wp = cq.Workplane("XZ")

# Create outer circle
wp = wp.moveTo(0, 0).circle(outer_radius)

# Create inner circle (cutout)
wp = wp.moveTo(0, 0).circle(inner_radius)

# Extrude along the normal (Y direction) by the given distance
# The design plan specifies direction = +w, which is [0,1,0]
result = wp.extrude(extrude_distance)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
