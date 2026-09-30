import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\106817_bb28b7aa_0004\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

os.makedirs(OUT_DIR, exist_ok=True)

# Washer parameters from the design plan
outer_radius = 5.5372
inner_radius = 1.9812
thickness = 1.3208

# Build the washer as an extruded annulus
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(thickness)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
