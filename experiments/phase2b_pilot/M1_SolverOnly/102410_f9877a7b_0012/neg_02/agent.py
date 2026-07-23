import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\102410_f9877a7b_0012\neg_02/generated.step"

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# Create an extruded annulus (bearing-like part)
# Outer radius: 6.0 mm, Inner radius: 4.25 mm, Extrude distance: 12.0 mm
# The design plan specifies the extrusion direction is +w (which maps to +Y in the part_local frame)
# We construct the annulus on the XZ plane and extrude along Y to match the frame mapping.

result = (
    cq.Workplane("XZ")
    .circle(6.0)
    .circle(4.25)
    .extrude(12.0)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
