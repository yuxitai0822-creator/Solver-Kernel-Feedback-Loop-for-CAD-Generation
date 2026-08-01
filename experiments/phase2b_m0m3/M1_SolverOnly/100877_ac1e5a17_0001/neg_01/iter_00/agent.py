import cadquery as cq
from cadquery import exporters

# Design Plan: Backing v1 - flat rectangular plate
# Dimensions: 279.4 mm x 215.9 mm x 1.5875 mm (extrude distance)
# The perturbation changed extrude depth from 0.15875 cm (1.5875 mm) to 0.238125 cm (2.38125 mm)
# But the design plan specifies 1.5875 mm, so we use the design plan value.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100877_ac1e5a17_0001\neg_01\iter_00/generated.step"

# Create the base workplane
wp = cq.Workplane("XY")

# Build the rectangle profile: 279.4 mm x 215.9 mm
# The rectangle is centered at origin for simplicity
result = wp.rect(279.4, 215.9).extrude(1.5875)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
