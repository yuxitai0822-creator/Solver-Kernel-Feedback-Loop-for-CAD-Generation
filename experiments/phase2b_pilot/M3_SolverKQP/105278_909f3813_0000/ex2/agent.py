import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\105278_909f3813_0000\ex2/generated.step"

os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# Build a rectangular prism with dimensions 12.0 (X) x 40.0 (Y) x 60.0 (Z)
# The design plan specifies an extruded rectangle with length_u=12.0, width_v=60.0, and extrude_distance=40.0
# Frame axes: u=(1,0,0) -> X, v=(0,0,-1) -> -Z, w=(0,1,0) -> Y
# This maps the profile rectangle (12 x 60) to the XZ plane, extruded along Y by 40

result = (
    cq.Workplane("XZ")
    .rect(12.0, 60.0)
    .extrude(40.0)
)

cq.exporters.export(result, OUT_STEP_PATH)