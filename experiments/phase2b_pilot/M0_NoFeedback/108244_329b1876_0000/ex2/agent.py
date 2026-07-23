import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\108244_329b1876_0000\ex2'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')
os.makedirs(OUT_DIR, exist_ok=True)

# Dimensions from the design plan
length_u = 1219.2  # mm
width_v = 2590.8   # mm
extrude_distance = 44.45  # mm

# Build the extruded rectangle
# The frame maps u->X, v->Z (downward in world, but we use positive Z for extrusion), w->Y
# We create the rectangle in the XZ plane and extrude along Y
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
