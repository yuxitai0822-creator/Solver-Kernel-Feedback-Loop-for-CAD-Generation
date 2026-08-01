import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Drone Leg - square strut
# Dimensions: 19.0 x 19.0 x 130.0 mm (rectangle profile extruded)
# The perturbed history had incorrect scaling (cm->mm x10) and wrong extent
# We reconstruct from the design plan directly

# Profile rectangle dimensions (from design plan)
length_u = 19.0  # mm
width_v = 19.0   # mm
extrude_distance = 130.0  # mm

# Build the part
result = (cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0006\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
