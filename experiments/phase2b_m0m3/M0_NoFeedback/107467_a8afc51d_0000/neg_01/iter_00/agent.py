import cadquery as cq
from cadquery import exporters

# Design Plan: extruded circle (disk)
# - Circle radius: 3.0 mm
# - Extrude distance: 14.0 mm (from explicit dimension, not the perturbed 21.0)
# - Direction: +Z (one side)
# - Result: single solid body

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\107467_a8afc51d_0000\neg_01\iter_00/generated.step"

# Build the disk: circle on XY plane, extrude along +Z
result = (
    cq.Workplane("XY")
    .circle(3.0)          # radius = 3.0 mm
    .extrude(14.0)        # extrude distance = 14.0 mm
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
