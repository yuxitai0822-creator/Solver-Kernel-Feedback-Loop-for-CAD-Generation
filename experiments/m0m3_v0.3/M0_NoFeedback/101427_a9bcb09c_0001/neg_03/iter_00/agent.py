import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0001\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: from (-2.5, 57.5) to (195.5, -2.5) in UV plane
# Inner rectangle: from (0.0, 55.0) to (193.0, 0.0) in UV plane
# Extrude 25.0 mm in +w direction (which is +Y in world)
# Note: UV coordinates are in mm, already converted from cm (x10)

# Build the outer rectangle
outer = cq.Workplane("XZ").moveTo(-2.5, 57.5).lineTo(-2.5, -2.5).lineTo(195.5, -2.5).lineTo(195.5, 57.5).close()

# Build the inner rectangle (hole)
inner = cq.Workplane("XZ").moveTo(0.0, 55.0).lineTo(0.0, 0.0).lineTo(193.0, 0.0).lineTo(193.0, 55.0).close()

# Extrude the outer profile 25 mm in +Y direction
result = outer.extrude(25.0)

# Cut the inner hole by extruding the inner profile and subtracting
cut_prism = inner.extrude(25.0)
result = result.cut(cut_prism)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
