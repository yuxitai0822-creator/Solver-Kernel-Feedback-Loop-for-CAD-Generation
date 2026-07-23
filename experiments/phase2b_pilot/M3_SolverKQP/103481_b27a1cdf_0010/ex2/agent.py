import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\103481_b27a1cdf_0010\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Build a rectangular prism based on the design plan
# Profile: rectangle centered at origin with length_u = 101.6 and width_v = 101.6
# Extrude: distance = 38.1 along +w (Z axis)

result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)
    .extrude(38.1)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
