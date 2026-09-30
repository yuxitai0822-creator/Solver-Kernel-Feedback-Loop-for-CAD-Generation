import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan (unit: mm)
# Outer radius: 5.5372 mm
# Inner radius: 1.9812 mm
# Extrude distance: 1.3208 mm
# Center in UV frame: (-25.400001, 12.7) but we'll center at origin for simplicity

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0004\neg_01\iter_00/generated.step"

# Create the washer as an extruded annulus
# Workplane: XZ plane (as in original script)
wp = cq.Workplane("XZ")

# Build outer circle
outer = wp.moveTo(0, 0).circle(5.5372)

# Build inner circle (cutout)
inner = wp.moveTo(0, 0).circle(1.9812)

# Create the washer by extruding the outer circle and cutting the inner circle
# Extrude distance: 1.3208 mm in the +Y direction (normal to XZ plane)
result = outer.extrude(1.3208)

# Cut the inner hole
# Create a cutting prism from the inner circle, extruded slightly more than the body
cut_prism = inner.extrude(1.3208 * 1.5)
result = result.cut(cut_prism)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
