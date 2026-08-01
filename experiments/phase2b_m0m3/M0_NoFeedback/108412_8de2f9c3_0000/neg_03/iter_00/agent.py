import cadquery as cq
from cadquery import exporters
import math

# Design Plan: flat_plate_or_panel, extruded rectangle
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The profile rectangle is centered at origin with corners at (±1219.2, ±609.6)
# Note: The design plan specifies rectangle corners at (±121.92, ±60.96) in cm, 
# but the dimensions table says 2438.4 x 1219.2 mm (which is 10x larger).
# The perturbation description says original=121.92, perturbed=97.536 (cm?)
# We use the explicit dimensions from the design plan: 2438.4 x 1219.2 x 12.7 mm

# Build the plate centered on the XY plane
result = (
    cq.Workplane("XY")
    .rect(2438.4, 1219.2, centered=True)
    .extrude(12.7)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108412_8de2f9c3_0000\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)