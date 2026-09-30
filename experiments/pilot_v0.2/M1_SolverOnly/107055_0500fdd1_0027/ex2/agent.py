import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\107055_0500fdd1_0027\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

os.makedirs(OUT_DIR, exist_ok=True)

# Washer dimensions (converted from cm to mm as noted in compiler_notes)
outer_radius = 3.49
inner_radius = 2.0
thickness = 0.36

# Build washer as an extruded annulus
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(thickness)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
