import cadquery as cq
from cadquery import exporters

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm
# Unit conversion note: original design was in cm, converted to mm

# Define dimensions in mm
length_u = 279.4  # X direction
width_v = 215.9   # Y direction
extrude_distance = 1.5875  # Z direction (thickness)

# Build the rectangular plate
# Start with a workplane on XY plane
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)  # Create rectangle centered at origin
    .extrude(extrude_distance)  # Extrude in +Z direction
)

# Export to STEP file
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100877_ac1e5a17_0001\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
