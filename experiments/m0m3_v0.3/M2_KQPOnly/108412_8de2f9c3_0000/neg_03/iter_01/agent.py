import cadquery as cq
from cadquery import exporters

# Design Plan: flat_plate_or_panel, extruded rectangle
# Dimensions: length_u=2438.4 mm, width_v=1219.2 mm, extrude_distance=12.7 mm
# Profile rectangle corners in UV: (121.92, -60.96), (121.92, 60.96), (-121.92, 60.96), (-121.92, -60.96)
# The UV coordinates are in cm (121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm)
# The perturbation description says original=121.92, perturbed=97.536 (cm)
# So perturbed half-dimensions: 97.536 cm = 975.36 mm (u), 60.96 cm = 609.6 mm (v) - v is unchanged
# But the design plan validation expects length_u=2438.4 and width_v=1219.2
# The perturbation only changes the u dimension from 121.92 to 97.536 cm
# So the perturbed rectangle is: 2*975.36 = 1950.72 mm (u) x 2*609.6 = 1219.2 mm (v)
# However, the kernel feedback shows expected u=2438.4, v=1219.2
# This means the perturbation should NOT be applied - we need to match the design plan exactly
# The design plan says length_u=2438.4, width_v=1219.2, extrude=12.7
# So we use the original dimensions: 2438.4 x 1219.2 x 12.7 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108412_8de2f9c3_0000\neg_03\iter_01/generated.step"

# Build the plate with exact design plan dimensions
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(2438.4, 1219.2)  # exact dimensions from design plan: length_u=2438.4, width_v=1219.2
    .extrude(12.7)  # thickness = 12.7 mm
)

exporters.export(result, OUT_STEP_PATH)