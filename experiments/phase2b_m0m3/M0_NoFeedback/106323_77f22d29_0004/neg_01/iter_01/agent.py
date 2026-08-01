import cadquery as cq
from cadquery import exporters

# Design Plan: bearing 2 v1
# Extruded annulus: outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm
# Perturbation: OneSide extent (extrude in +Z direction only, not symmetric)
# The original design had symmetric extrusion (both sides), but perturbation changes to one-side.
# Since the design plan says symmetric but perturbation says one-side, we follow the perturbation.
# The script must produce a valid STEP file.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106323_77f22d29_0004\neg_01\iter_01/generated.step"

# Build the annulus using a single workplane and proper cadquery operations
# Outer circle radius = 17.5 mm, inner circle radius = 12.5 mm
# Extrude one-side (positive Z) by total distance 10.0 mm

# Create workplane on XY plane
result = (cq.Workplane("XY")
          .circle(17.5)  # outer circle
          .circle(12.5)  # inner circle (creates a hole automatically)
          .extrude(10.0)  # extrude one-side by 10.0 mm
         )

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
