import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\106817_bb28b7aa_0002\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

os.makedirs(OUT_DIR, exist_ok=True)

# Thumb screw: extruded circle (disk)
# Radius: 4.87045 mm, Extrude height: 6.8707 mm
# Origin at bbox_min_corner, so center is offset in XY by radius

radius = 4.87045
height = 6.8707

result = (cq.Workplane("XY")
          .circle(radius)
          .extrude(height))

# Translate so the bounding box minimum corner is at the origin
# By default, the circle is centered at (0,0) and extruded from z=0 to z=height
# The bbox min is at (-radius, -radius, 0)
# We shift by (+radius, +radius, 0) to place bbox_min at (0,0,0)
result = result.translate((radius, radius, 0))

cq.exporters.export(result, OUT_STEP_PATH)
