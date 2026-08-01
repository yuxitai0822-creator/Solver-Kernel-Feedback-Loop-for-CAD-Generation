import cadquery as cq
from cadquery import exporters

# Design Plan: flat plate/panel, extruded rectangle
# Dimensions: length_u=254.0 mm, width_v=190.5 mm, extrude_distance=3.175 mm
# The previous script used 4.7625 mm (perturbed value). We restore the correct value.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0017\neg_01\iter_00\generated.step"

# Build the rectangle profile
# The profile curves define a rectangle from (0,0) to (25.4, 19.05) in UV space
# But the dimensions table says length_u=254.0, width_v=190.5 (scaled by 10 from cm to mm)
# The curves use 25.4 and 19.05 which are 1/10 of the actual dimensions.
# This is because the original source was in cm and converted to mm (x10).
# The curves in the design plan show: 0.0,19.05 -> 0.0,0.0 -> 25.4,0.0 -> 25.4,19.05 -> 0.0,19.05
# These are in mm after conversion. But the dimensions table says 254.0 and 190.5.
# There's a discrepancy: the curves are 1/10 of the stated dimensions.
# The compiler notes say "unit_conversion_applied: cm_to_mm (x10)".
# The curves likely represent the original cm values (2.54 cm x 1.905 cm) which become 25.4 mm x 19.05 mm.
# But the dimensions table says 254.0 x 190.5. This is inconsistent.
# Looking at the perturbation description: original extrude=0.3175, perturbed=0.47625 (in cm?)
# The previous script used EXTENT_TOTAL_MM = 4.7625 which is 0.47625*10.
# The design plan says extrude_distance = 3.175 mm (which is 0.3175*10).
# So the correct extrude is 3.175 mm.
# For the rectangle, the curves use 25.4 and 19.05 which match the design plan curves.
# The dimensions table values (254.0, 190.5) seem to be a different interpretation.
# We'll use the curve values directly as they match the profile definition.

# Create workplane
wp = cq.Workplane("XY")

# Build rectangle from the 4 corner points
# Start at (0, 19.05), go to (0, 0), then (25.4, 0), then (25.4, 19.05), close back to (0, 19.05)
wp = wp.moveTo(0, 19.05)
wp = wp.lineTo(0, 0)
wp = wp.lineTo(25.4, 0)
wp = wp.lineTo(25.4, 19.05)
wp = wp.close()

# Extrude by 3.175 mm in +Z direction
result = wp.extrude(3.175)

# Export
importers.export(result, OUT_STEP_PATH)
