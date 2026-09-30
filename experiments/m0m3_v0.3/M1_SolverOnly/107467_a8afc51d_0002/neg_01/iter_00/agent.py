import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Pivot - disk with radius 3.0 mm, extrude 25.0 mm
# Perturbation: extrude depth changed from 2.5 cm (25 mm) to 3.75 cm (37.5 mm)
# But the design plan specifies 25.0 mm, so we follow the design plan.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107467_a8afc51d_0002\neg_01\iter_00/generated.step"

# Create a simple disk: circle radius 3.0 mm, extruded 25.0 mm
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius from design plan
    .extrude(25.0)  # extrude distance from design plan
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
