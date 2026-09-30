import cadquery as cq
import os

OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\106817_bb28b7aa_0002\ex2'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')

os.makedirs(OUT_DIR, exist_ok=True)

# Build the thumb screw disk as an extruded circle
# Radius: 4.87045 mm, Extrude height: 6.8707 mm
# Origin convention: bbox_min_corner, so the circle is centered at (0, 0) on the XY plane
# and extruded in the +Z direction.

result = (
    cq.Workplane("XY")
    .circle(4.87045)
    .extrude(6.8707)
)

cq.exporters.export(result, OUT_STEP_PATH)
