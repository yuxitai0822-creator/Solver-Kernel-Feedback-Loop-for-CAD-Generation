import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0004\neg_01\iter_00\generated.step"

# Design parameters from the design plan (converted from cm to mm where needed)
# Outer radius: 5.5372 mm (already in mm)
# Inner radius: 1.9812 mm (already in mm)
# Center: (-25.400001, 12.7) mm
# Extrude distance: 1.3208 mm (the design plan says 1.3208, not the perturbed 1.9812)
# The perturbation description says original=0.13208 cm = 1.3208 mm, perturbed=0.19812 cm = 1.9812 mm
# But the design plan explicitly states extrude_distance = 1.3208 mm, so we use that.

outer_radius = 5.5372
inner_radius = 1.9812
center_x = -25.400001
center_y = 12.7
extrude_distance = 1.3208  # mm (from design plan)

# Build the washer using cadquery
# Workplane is XZ according to the previous script, but we need to orient correctly
# The design plan says: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means: sketch on XZ plane, extrude along Y (w direction)

# Create the outer circle
result = (cq.Workplane("XZ")
    .moveTo(center_x, center_y)
    .circle(outer_radius)
    .extrude(extrude_distance))

# Cut the inner hole
inner_cut = (cq.Workplane("XZ")
    .moveTo(center_x, center_y)
    .circle(inner_radius)
    .extrude(extrude_distance))

result = result.cut(inner_cut)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
