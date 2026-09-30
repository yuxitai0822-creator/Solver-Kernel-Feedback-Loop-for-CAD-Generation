import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\107055_0500fdd1_0027\ex2/generated.step"

# Washer dimensions (converted from cm to mm as noted in compiler_notes)
outer_radius = 3.49
inner_radius = 2.0
thickness = 0.36

# Build the washer as an extruded annulus
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(thickness)
)

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# Export the result to STEP
cq.exporters.export(result, OUT_STEP_PATH)
