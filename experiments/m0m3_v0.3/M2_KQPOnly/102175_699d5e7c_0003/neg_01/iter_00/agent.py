import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102175_699d5e7c_0003\neg_01\iter_00\generated.step"

# Design Plan: rectangular prism, 39.0 x 68.0 x 10.0 mm
# Profile rectangle corners in UV: (-3.9, 6.8) to (0.0, 0.0) in cm -> mm: (-39, 68) to (0, 0)
# Extrude distance: 10.0 mm (from design plan, not the perturbed 15.0)

# Build the rectangle on XY plane
result = (
    cq.Workplane("XY")
    .moveTo(-39.0 / 2, 68.0 / 2)  # center at (-19.5, 34.0)
    .rect(39.0, 68.0, centered=True)
    .extrude(10.0)
)

# Export STEP
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")