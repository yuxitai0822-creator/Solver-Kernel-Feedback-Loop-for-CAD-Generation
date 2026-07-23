import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\106323_77f22d29_0004\neg_01/generated.step"

# Create an extruded annulus (bearing)
# Outer radius: 17.5 mm, Inner radius: 12.5 mm
# Extrude distance: 10.0 mm, symmetric (both sides)

result = (
    cq.Workplane("XY")
    .circle(17.5)
    .circle(12.5)
    .extrude(10.0 / 2.0, both=True)
)

# Ensure the output directory exists
out_dir = os.path.dirname(OUT_STEP_PATH)
if out_dir and not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)

# Export the result to STEP
cq.exporters.export(result, OUT_STEP_PATH)
