import cadquery as cq
from cadquery import exporters

# Design Plan: flat rectangular plate 254.0 x 190.5 x 3.175 mm
# The previous script used a perturbed extrusion depth of 4.7625 mm (0.47625 cm).
# The design plan specifies 3.175 mm (0.3175 cm).
# We rebuild from scratch using the correct dimensions.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100877_ac1e5a17_0017\neg_01\iter_00/generated.step"

# Dimensions from design plan (in mm)
length_u = 254.0  # along x
width_v = 190.5   # along y
extrude_depth = 3.175  # along z

# Build the plate centered on the XY plane for simplicity
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_depth)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
