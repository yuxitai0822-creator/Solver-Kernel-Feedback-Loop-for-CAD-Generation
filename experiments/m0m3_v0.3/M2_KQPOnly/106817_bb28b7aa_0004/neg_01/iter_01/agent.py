import cadquery as cq
from cadquery import exporters

# Design parameters from the design plan (unit: mm)
# Outer radius: 5.5372 mm
# Inner radius: 1.9812 mm
# Extrude distance: 1.3208 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0004\neg_01\iter_01/generated.step"

# Create the washer as an extruded annulus using a single workplane operation
# Workplane: XY plane (standard for extrusion along Z)
result = (
    cq.Workplane("XY")
    .circle(5.5372)  # outer circle
    .circle(1.9812)  # inner circle (creates a hole)
    .extrude(1.3208)  # extrude along Z
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
