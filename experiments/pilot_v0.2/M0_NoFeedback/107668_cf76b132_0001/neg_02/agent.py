import cadquery as cq
import os

OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\107668_cf76b132_0001\neg_02'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')

# Create an extruded annulus (bearing/wheel)
# Outer radius: 132.5 mm, Inner radius: 75.0 mm
# Extrude distance: 100.0 mm along +X axis (w_dir)

result = (
    cq.Workplane("YZ")
    .circle(132.5)
    .circle(75.0)
    .extrude(100.0)
)

# Ensure output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
