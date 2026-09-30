import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 17.5 mm, Inner radius = 12.5 mm, Total extrusion = 10.0 mm (symmetric)
# Unit conversion: cm->mm already applied (radii are in mm)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106323_77f22d29_0004\neg_03\iter_00/generated.step"

# Build the annulus profile on XY plane
result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer radius
    .circle(12.5)  # inner radius (creates a hole)
    .extrude(10.0, both=True)  # symmetric extrusion, total 10 mm
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
