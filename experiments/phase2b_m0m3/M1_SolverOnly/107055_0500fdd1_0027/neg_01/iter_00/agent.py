import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Washer (2)
# Extruded annulus with outer radius 3.49 mm, inner radius 2.0 mm, thickness 0.36 mm
# The previous script used perturbed value 0.5399999999999999 mm (from cm conversion)
# but the design plan specifies 0.36 mm. We use the design plan value.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\107055_0500fdd1_0027\neg_01\iter_00/generated.step"

# Parameters from design plan
outer_radius = 3.49  # mm
inner_radius = 2.0   # mm
thickness = 0.36     # mm

# Build the washer using cadquery
# Create the outer circle
result = (cq.Workplane("XY")
          .circle(outer_radius)
          .extrude(thickness))

# Cut the inner hole
inner_cut = (cq.Workplane("XY")
             .circle(inner_radius)
             .extrude(thickness))

result = result.cut(inner_cut)

# Export to STEP
importers.export(result, OUT_STEP_PATH)
