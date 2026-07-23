import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\106817_bb28b7aa_0002\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters
# Radius: 4.87045 mm (from dimensions section, overriding profiles section)
# Extrude distance: 6.8707 mm
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
# Extrude direction: +w (which maps to +Y in world coordinates)
# Origin convention: bbox_min_corner

radius = 4.87045
extrude_distance = 6.8707

# Build the extruded circle (cylinder)
# The circle is centered at (0, 0) on the sketch plane.
# Sketch plane is defined by u and v directions: u=(1,0,0) -> X, v=(0,0,-1) -> -Z
# This corresponds to cadquery's 'XZ' plane (normal is Y, which aligns with w=(0,1,0))
# Extrude direction +w = +Y

result = (cq.Workplane("XZ")
          .circle(radius)
          .extrude(extrude_distance))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
