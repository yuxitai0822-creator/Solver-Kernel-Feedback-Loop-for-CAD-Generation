import cadquery as cq
import os

OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\107668_cf76b132_0001\ex2'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')

os.makedirs(OUT_DIR, exist_ok=True)

# Create an extruded annulus (tube/bearing shape)
# Outer radius: 132.5 mm, Inner radius: 75.0 mm
# Extrude distance: 100.0 mm along +X axis (w_dir)

result = (
    cq.Workplane("XZ")
    .circle(132.5)
    .circle(75.0)
    .extrude(100.0)
)

cq.exporters.export(result, OUT_STEP_PATH)