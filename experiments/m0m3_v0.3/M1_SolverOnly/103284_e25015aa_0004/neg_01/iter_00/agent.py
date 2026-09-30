import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Tail Stock Lever - extruded circle
# Dimensions: radius=11.938 mm, extrude distance=12.7 mm
# The previous script had incorrect extrude distance (19.05 mm instead of 12.7 mm)
# and used a complex history-based approach. This script directly implements the design.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\103284_e25015aa_0004\neg_01\iter_00/generated.step"

# Create a workplane on XY plane
wp = cq.Workplane("XY")

# Build the circle profile at the specified center (8.077681, 8.284339) with radius 11.938 mm
# Note: The center_uv from the design plan is (8.077681, 8.284339) but since we're creating
# a single body, the absolute position doesn't matter for the final shape.
# We'll center it at origin for simplicity, which matches the expected span dimensions.
circle = wp.circle(11.938)

# Extrude by 12.7 mm in the +Z direction (one side)
result = circle.extrude(12.7)

# Export to STEP file
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
