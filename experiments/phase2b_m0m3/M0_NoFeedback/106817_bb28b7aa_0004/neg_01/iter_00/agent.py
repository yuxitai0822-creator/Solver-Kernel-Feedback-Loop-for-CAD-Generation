import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0004\neg_01\iter_00\generated.step"

# Design parameters from the design plan (converted to mm)
# Outer radius: 5.5372 mm
# Inner radius: 1.9812 mm
# Center in UV plane: (-2.540000081062317, 1.2700000405311584) mm
# Extrude distance: 1.3208 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]

# Build the washer on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
# The center is at (-2.540000081062317, 1.2700000405311584) in UV coordinates
# U corresponds to X, V corresponds to Z (since v_dir = [0,0,-1])

center_x = -2.540000081062317
center_z = 1.2700000405311584  # V coordinate maps to Z
outer_radius = 5.5372
inner_radius = 1.9812
extrude_distance = 1.3208

# Create workplane on XZ plane
result = (
    cq.Workplane("XZ")
    .moveTo(center_x, center_z)
    .circle(outer_radius)
    .extrude(extrude_distance)
)

# Cut the inner hole
inner_cut = (
    cq.Workplane("XZ")
    .moveTo(center_x, center_z)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

result = result.cut(inner_cut)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
