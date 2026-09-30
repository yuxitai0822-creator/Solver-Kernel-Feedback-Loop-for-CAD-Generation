import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular frame (hollow box) with outer 500x300 mm, inner 400x200 mm, extruded 500 mm
# The kernel feedback expects through_void_count = 1, so we must create the hollow frame (not a solid block)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0006\neg_03\iter_02\generated.step"

# Build the hollow rectangular frame:
# Outer rectangle: 500 x 300 mm
# Inner rectangle: 400 x 200 mm (offset 50 mm from outer edges on each side)
# Extrude 500 mm in +Z direction

result = (
    cq.Workplane("XY")
    .center(250, 150)  # center of outer rectangle
    .rect(500, 300)    # outer profile
    .extrude(500)      # extrude to full height
    .faces(">Z")       # select top face
    .workplane()
    .center(250, 150)  # center of inner rectangle (same center)
    .rect(400, 200)    # inner profile
    .cutThruAll()      # cut through the entire block to create the void
)

exporters.export(result, OUT_STEP_PATH)