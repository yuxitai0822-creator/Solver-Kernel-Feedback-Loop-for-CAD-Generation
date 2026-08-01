import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle plate
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The perturbation description says E2_extrude_depth original=1.27, perturbed=1.905 (cm)
# But the design plan explicitly states 12.7 mm for extrude distance.
# The previous script used 19.05 mm (1.905 cm) which is the perturbed value.
# We must follow the design plan which says 12.7 mm.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108412_8de2f9c3_0000\neg_01\iter_00/generated.step"

# Create the rectangle profile centered at origin
# The design plan gives coordinates in UV space: u from -121.92 to 121.92, v from -60.96 to 60.96
# But the dimensions say length_u = 2438.4 mm and width_v = 1219.2 mm
# The UV coordinates appear to be in cm (121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm)
# So the rectangle spans from -1219.2 to 1219.2 in x, and -609.6 to 609.6 in y

# Build the plate
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(2438.4, 1219.2)
    .extrude(12.7)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
