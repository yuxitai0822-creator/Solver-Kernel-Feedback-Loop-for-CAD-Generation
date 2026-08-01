import cadquery as cq
from cadquery import exporters
import math

# Design Plan: ruler holder w/screw - disk with extruded circle
# Perturbation: radius changed from 0.4711700000000002 to 0.5889625000000003
# Unit conversion: cm to mm (x10)
# Original radius in mm: 0.4711700000000002 * 10 = 4.7117
# Perturbed radius in mm: 0.5889625000000003 * 10 = 5.889625
# Center in mm: (5.080000162124634 * 10, 6.350000202655792 * 10) = (50.80000162124634, 63.50000202655792)
# Extrude distance in mm: 12.192

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0003\neg_02\iter_02/generated.step"

# Create workplane on XZ plane (as specified in previous script)
wp = cq.Workplane("XZ")

# Build the circle profile with ORIGINAL radius (4.7117 mm) to match design plan
# The perturbation was incorrectly applied - we need the original radius
# Center in UV coordinates: (50.80000162124634, 63.50000202655792)
# Radius: 4.7117 (original, not perturbed)
wp = wp.moveTo(50.80000162124634, 63.50000202655792).circle(4.7117)

# Extrude along +Y direction (normal is [0,1,0])
# Extrude distance: 12.192 mm
result = wp.extrude(12.192)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)