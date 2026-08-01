import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u = 193.0 mm, width_v = 55.0 mm, extrude_distance = 50.0 mm
# Note: The design plan shows length_u=1930.0 and width_v=550.0, but the curves show 193.0 and 55.0.
# The compiler notes indicate cm_to_mm conversion (x10), so the actual values are 193.0 and 55.0.
# The perturbation description says original=55.0, perturbed=44.0, but the design plan still shows 55.0.
# We follow the design plan curves which define the actual geometry.

# Create the rectangle on the XZ plane (as per previous script's WORKPLANE = 'XZ')
# The rectangle spans from (0,0) to (193.0, 55.0) in UV coordinates
# U direction = X axis, V direction = Z axis (negative), W direction = Y axis
# So rectangle is in XZ plane, extruded along Y axis

result = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .rect(193.0, 55.0, centered=False)
    .extrude(50.0)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0002\neg_03\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)