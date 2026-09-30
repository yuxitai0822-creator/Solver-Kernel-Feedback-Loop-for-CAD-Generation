import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
OUTER_RADIUS = 0.43625  # perturbed radius (original 0.349 -> 0.43625)
INNER_RADIUS = 0.2      # inner radius
EXTRUDE_DISTANCE = 0.36  # total extrusion distance in mm

# Output path
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107055_0500fdd1_0027\neg_02\iter_00/generated.step"

# Build the washer using cadquery
# Start with a workplane on the XY plane
result = (
    cq.Workplane("XY")
    .circle(OUTER_RADIUS)  # outer circle
    .circle(INNER_RADIUS)  # inner circle (creates a hole)
    .extrude(EXTRUDE_DISTANCE)  # extrude to create the washer
)

# Export the result to STEP file
exporters.export(result, OUT_STEP_PATH)
