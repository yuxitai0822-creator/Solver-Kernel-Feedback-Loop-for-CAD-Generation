import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108850_0dcd5ef1_0002\neg_01\iter_00\generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion):
# Rectangle: 171.45 mm x 38.1 mm (length_u x width_v)
# Extrude distance: 6.35 mm (original was 0.635 cm = 6.35 mm; perturbation changed to 0.9525 cm = 9.525 mm)
# The perturbation description says: operator=E2_extrude_depth; original=0.635; perturbed=0.9525
# So we use 9.525 mm for the extrude depth.

# Build the rectangle on the XZ plane (as per previous script's WORKPLANE = 'XZ')
# The profile curves in the design plan show:
# start_uv: (0.0, 3.81) -> (0.0, 0.0) -> (17.145, 0.0) -> (17.145, 3.81) -> back to (0.0, 3.81)
# But the dimensions say length_u = 171.45, width_v = 38.1
# The curves appear to be in cm (17.145 cm = 171.45 mm, 3.81 cm = 38.1 mm)
# So we use the mm values directly.

# Create workplane on XZ (since previous script used XZ)
wp = cq.Workplane("XZ")

# Draw rectangle centered at origin, 171.45 mm along X, 38.1 mm along Z
# The rectangle spans from (0,0) to (171.45, 38.1) in the sketch plane
# We'll center it for simplicity, then extrude along Y (the normal of XZ plane)
result = wp.center(171.45/2, 38.1/2).rect(171.45, 38.1).extrude(9.525)

# Export
importers.export(result, OUT_STEP_PATH)
