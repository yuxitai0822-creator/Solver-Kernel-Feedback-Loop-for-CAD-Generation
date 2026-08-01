import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
OUTER_RADIUS = 6.0  # mm (from 0.6000000000000002 cm * 10)
INNER_RADIUS = 4.25  # mm (from 0.4250000000000001 cm * 10)
EXTRUDE_HEIGHT = 12.0  # mm (from 1.2 cm * 10, original value before perturbation)

# Output path
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102410_f9877a7b_0012\neg_01\iter_00\generated.step"

# Build the part
# Create a workplane on the XZ plane (as specified in the design plan's frame)
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the sketch plane is XZ (u=x, v=z) and extrusion is along Y (w=y)
result = (
    cq.Workplane("XZ")
    .circle(OUTER_RADIUS)  # Outer circle
    .circle(INNER_RADIUS)  # Inner circle (hole)
    .extrude(EXTRUDE_HEIGHT)  # Extrude along Y (positive direction)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
