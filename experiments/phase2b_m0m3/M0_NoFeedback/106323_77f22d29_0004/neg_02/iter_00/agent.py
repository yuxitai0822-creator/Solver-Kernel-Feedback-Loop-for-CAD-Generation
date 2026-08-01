import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 17.5 mm, Inner radius = 12.5 mm, Total height = 10.0 mm (symmetric)
# The previous script had incorrect outer radius (21.875 instead of 17.5) and inner radius (12.5 correct)
# Also had complex unnecessary logic for reading JSON history file that may not exist

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106323_77f22d29_0004\neg_02\iter_00\generated.step"

# Parameters from design plan (converted cm->mm, radii already in mm)
outer_radius = 17.5  # mm
inner_radius = 12.5  # mm
total_height = 10.0  # mm (symmetric extrusion)

# Build the annulus
# Start with outer circle, extrude, then cut inner circle
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .extrude(total_height / 2, both=True)  # symmetric extrusion
    .faces("<Z")  # select bottom face to cut from
    .workplane()
    .circle(inner_radius)
    .cutThruAll()  # cut through the entire body
)

# Export STEP file
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
