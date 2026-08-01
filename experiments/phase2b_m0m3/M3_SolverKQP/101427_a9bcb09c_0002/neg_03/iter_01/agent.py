import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u = 1930.0 mm, width_v = 550.0 mm, extrude_distance = 50.0 mm
# The design plan explicitly states length_u=1930.0 and width_v=550.0 in the dimensions section.
# The compiler notes indicate cm_to_mm conversion (x10), but the dimensions are already in mm.
# The curves in the profiles show 193.0 and 55.0, but those are in UV space (which may be in cm).
# The validation intents expect spans of 1930.0, 550.0, and 50.0.
# The previous iteration failed because it used 193.0 and 55.0 instead of 1930.0 and 550.0.
# We follow the explicit dimensions from the design plan: 1930.0 x 550.0 mm, extruded 50.0 mm.

# Create the rectangle on the XZ plane (as per previous script's WORKPLANE = 'XZ')
# The rectangle spans from (0,0) to (1930.0, 550.0) in UV coordinates
# U direction = X axis, V direction = Z axis (negative), W direction = Y axis
# So rectangle is in XZ plane, extruded along Y axis

result = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .rect(1930.0, 550.0, centered=False)
    .extrude(50.0)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0002\neg_03\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)