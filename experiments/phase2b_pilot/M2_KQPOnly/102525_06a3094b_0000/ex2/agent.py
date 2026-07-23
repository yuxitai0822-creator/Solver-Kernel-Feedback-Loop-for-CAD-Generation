import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\102525_06a3094b_0000\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# SOIC-8 package body: rectangular prism
# Dimensions from design plan (unit conversion cm->mm applied):
# length_u (along X) = 3.9 mm
# width_v (along Z) = 4.9 mm
# extrude_distance (along Y) = 1.55 mm

result = (
    cq.Workplane("XZ")
    .rect(3.9, 4.9)
    .extrude(1.55)
)

cq.exporters.export(result, OUT_STEP_PATH)