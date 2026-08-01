import cadquery as cq
from cadquery import exporters

# Design Plan: flat plate/panel, extruded rectangle
# Dimensions: length_u=254.0 mm, width_v=190.5 mm, extrude_distance=3.175 mm
# Note: The perturbed history JSON had incorrect y-coordinates (shifted by 152.4 mm).
# We build directly from the design plan dimensions for a clean, correct result.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100877_ac1e5a17_0017\neg_03\iter_00/generated.step"

# Create workplane on XY plane
wp = cq.Workplane("XY")

# Build rectangle centered at origin with dimensions from design plan
# length_u = 254.0 mm (along X), width_v = 190.5 mm (along Y)
result = wp.rect(254.0, 190.5, centered=True).extrude(3.175)

# Export to STEP
importers = None  # not needed
exporters.export(result, OUT_STEP_PATH)
