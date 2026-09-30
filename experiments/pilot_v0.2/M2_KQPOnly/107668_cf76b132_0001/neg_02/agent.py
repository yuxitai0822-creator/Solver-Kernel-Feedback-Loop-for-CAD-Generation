import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\107668_cf76b132_0001\neg_02"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

# Create an extruded annulus (bearing/wheel)
# Outer radius: 132.5 mm, Inner radius: 75.0 mm
# Extrude distance: 100.0 mm
# The design plan specifies the extrusion direction along +w (which maps to +X in the part_local frame)
# with the annulus lying in the YZ plane.

outer_radius = 132.5
inner_radius = 75.0
extrude_distance = 100.0

# Create the annulus on the YZ plane (normal is X) and extrude along +X
result = (
    cq.Workplane("YZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)
