import cadquery as cq
import os

OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\107668_cf76b132_0001\ex2'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')

os.makedirs(OUT_DIR, exist_ok=True)

# Create an extruded annulus (bearing/wheel shape)
# Outer radius: 132.5 mm, Inner radius: 75.0 mm
# Extrude distance: 100.0 mm along +Z axis
# The design plan specifies the extrusion direction as +w, where w_dir is [1, 0, 0] (X axis).
# However, the validation intents expect spans of 265mm along u and v, and 100mm along w.
# Since u_dir=[0,0,-1] and v_dir=[0,1,0], the 265mm spans correspond to Z and Y axes.
# The w_dir=[1,0,0] corresponds to the X axis, which should have the 100mm extrusion span.
# To satisfy the validation intents (span_x=100, span_y=265, span_z=265),
# we extrude the annulus along the X axis.

outer_radius = 132.5
inner_radius = 75.0
extrude_distance = 100.0

# Create the annulus on the YZ plane (normal is X) and extrude along +X
result = (cq.Workplane("YZ")
          .circle(outer_radius)
          .circle(inner_radius)
          .extrude(extrude_distance))

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)
