import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107668_cf76b132_0001\neg_02\iter_00\generated.step"

# Design parameters from the design plan
# Outer radius = 13.25 cm = 132.5 mm (after cm->mm conversion)
# Inner radius = 7.5 cm = 75.0 mm
# Extrude distance = 10.0 cm = 100.0 mm
# The frame has u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# This means the extrusion is along the x-axis (w_dir)
# The profile is on the YZ plane (u and v directions)

outer_radius = 132.5  # mm
inner_radius = 75.0   # mm
extrude_distance = 100.0  # mm

# Create the workplane on YZ plane (since extrusion is along X)
# The profile is centered at origin in UV space (center_uv = [0,0])
# U direction is [0,0,-1] (negative Z), V direction is [0,1,0] (positive Y)
# So the profile plane is YZ with center at origin

# Build the outer circle on YZ plane
result = (cq.Workplane("YZ")
          .circle(outer_radius)
          .extrude(extrude_distance))

# Cut the inner hole
inner_cut = (cq.Workplane("YZ")
             .circle(inner_radius)
             .extrude(extrude_distance))

result = result.cut(inner_cut)

# Export
importers = cq.exporters
exporters.export(result, OUT_STEP_PATH)
