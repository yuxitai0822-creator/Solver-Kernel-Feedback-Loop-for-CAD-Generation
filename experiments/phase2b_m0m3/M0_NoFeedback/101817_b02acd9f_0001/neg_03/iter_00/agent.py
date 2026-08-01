import cadquery as cq
from cadquery import exporters
import math

# Design Plan: horizontal leg 1
# Extruded rectangular frame with outer 40x40 mm and inner 37.6x37.6 mm, extruded 520 mm
# The perturbation removes the inner void (E4_void_remove), so we create a solid rectangular prism

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0001\neg_03\iter_00/generated.step"

# Create the outer rectangle profile (40x40 mm centered at origin)
# The design plan shows outer loop from (-4,4) to (0,4) etc. in UV space, but dimensions are 40x40
# The inner loop would be 37.6x37.6, but we omit it per perturbation (void removal)

result = (
    cq.Workplane("XY")
    .rect(40.0, 40.0, centered=True)
    .extrude(520.0)
)

# Export the result
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")