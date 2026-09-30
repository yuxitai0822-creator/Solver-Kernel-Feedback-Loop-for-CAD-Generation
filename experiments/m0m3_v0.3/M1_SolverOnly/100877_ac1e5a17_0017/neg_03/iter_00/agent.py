import cadquery as cq
from cadquery import exporters

# Design Plan: flat rectangular plate 254.0 x 190.5 x 3.175 mm
# The perturbation changes the rectangle's v-dimension from 190.5 to 152.4 mm
# (original 19.05 cm -> perturbed 15.24 cm, then converted to mm)

# Build the rectangle centered at origin for simplicity
# Dimensions in mm
length_u = 254.0  # along x
width_v = 152.4   # along y (perturbed from 190.5)
extrude_distance = 3.175  # along z

# Create the plate
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100877_ac1e5a17_0017\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
