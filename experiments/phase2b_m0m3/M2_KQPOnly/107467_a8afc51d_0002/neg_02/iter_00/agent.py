import cadquery as cq
from cadquery import exporters

# Design Plan: Pivot - a disk (extruded circle)
# Dimensions: radius = 3.0 mm, extrude distance = 25.0 mm
# The perturbation changed the radius from 0.3 to 0.375 in the profile curves,
# but the actual intended radius is 3.0 mm (from dimensions section).
# The profile curves radius (0.375) is the UV-space radius, not the actual 3D radius.
# We build the part directly from the explicit dimensions.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\107467_a8afc51d_0002\neg_02\iter_00\generated.step"

# Build the disk: circle with radius 3.0 mm, extruded 25.0 mm in +Z direction
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius from dimensions section
    .extrude(25.0)  # extrude distance from dimensions section
)

# Export to STEP
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
