import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\100877_ac1e5a17_0001\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Dimensions from the design plan (unit conversion cm_to_mm x10 was applied)
length_u = 279.4  # mm
width_v = 215.9   # mm
extrude_w = 1.5875  # mm

# Build the extruded rectangle
result = cq.Workplane("XY").rect(length_u, width_v).extrude(extrude_w)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
