import cadquery as cq
from cadquery import exporters

# Design Plan: SoapCutterBackBar1 v1
# Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
# The profile is a rectangle in the XZ plane (u along X, v along Z, extrude along Y)
# Profile coordinates from design plan (uv space):
#   (0.0, 5.08) -> (0.0, 0.0) -> (27.94, 0.0) -> (27.94, 5.08) -> back to start
# Note: The design plan dimensions show length_u=279.4, width_v=50.8
# The uv coordinates given are 27.94 x 5.08, which is 1/10 of the actual dimensions.
# This is because the original source was in cm and converted to mm (x10).
# The actual rectangle should be 279.4 mm x 50.8 mm.
# The uv coordinates in the design plan are in cm (27.94 cm = 279.4 mm, 5.08 cm = 50.8 mm).
# We'll build the rectangle directly with the correct mm dimensions.

# Build the rectangle in the XZ plane (u along X, v along Z)
# The rectangle spans from (0, 0) to (279.4, 50.8) in the XZ plane
# Extrude along Y (positive direction) by 19.05 mm

result = (
    cq.Workplane("XZ")
    .rect(279.4, 50.8, centered=False)
    .extrude(19.05)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0007\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)