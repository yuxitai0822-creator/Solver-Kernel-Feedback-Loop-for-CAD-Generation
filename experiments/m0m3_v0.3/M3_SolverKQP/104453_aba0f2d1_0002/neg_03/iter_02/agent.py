import cadquery as cq
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0002\neg_03\iter_02\generated.step"

# Design parameters from the design plan
# The plan's dimensions section is authoritative:
# straight_length=500.0, radius=50.0, extrude_distance=100.0
# The total span along u should be straight_length + 2*radius = 500 + 100 = 600
# The total span along v should be 2*radius = 100
straight_length = 500.0
radius = 50.0
extrude_distance = 100.0

# Build the stadium profile using native cadquery arc and line operations
# This ensures proper geometry rather than discretized points

# Create workplane
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(0, -radius)  # Start at bottom of left semicircle
    .threePointArc((radius, 0), (0, radius))  # Left semicircle (bottom to top)
    .lineTo(straight_length, radius)  # Top line
    .threePointArc((straight_length + radius, 0), (straight_length, -radius))  # Right semicircle (top to bottom)
    .lineTo(0, -radius)  # Bottom line back to start
    .close()
    .extrude(extrude_distance)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
