import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\102410_f9877a7b_0012\neg_01"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

os.makedirs(OUT_DIR, exist_ok=True)

# Create an extruded annulus (bearing-like shape)
# Outer radius: 6.0 mm, Inner radius: 4.25 mm, Extrude distance: 12.0 mm
# The design plan specifies the extrusion direction as +w, where w_dir is [0, 1, 0],
# meaning the extrusion happens along the Y axis.

result = (
    cq.Workplane("XZ")
    .circle(6.0)
    .circle(4.25)
    .extrude(12.0)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
