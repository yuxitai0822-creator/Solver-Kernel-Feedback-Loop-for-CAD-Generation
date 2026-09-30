import cadquery as cq
from cadquery import exporters

# Design Plan: flat rectangular plate
# Dimensions: length_u = 254.0 mm, width_v = 190.5 mm, extrude_distance = 3.175 mm
# The profile is a rectangle with corners at (0,0), (254,0), (254,190.5), (0,190.5)
# Note: The design plan specifies the rectangle in UV coordinates with start_uv and end_uv
# The UV coordinates given are: (0,19.05) -> (0,0) -> (25.4,0) -> (25.4,19.05) -> (0,19.05)
# But the dimensions table says length_u=254.0 and width_v=190.5
# The UV coordinates appear to be in cm (25.4 cm = 254 mm, 19.05 cm = 190.5 mm)
# So we use the dimensions from the table: 254.0 x 190.5 mm

# Build the plate
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5, centered=False)
    .extrude(3.175)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100877_ac1e5a17_0017\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)