import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\108851_4d515b10_0007\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters (converted from cm to mm as per compiler_notes)
length_u = 279.4  # mm
width_v = 50.8    # mm
extrude_distance = 19.05  # mm

# Build the extruded rectangle
# The frame defines u=(1,0,0), v=(0,0,-1), w=(0,1,0)
# This means the sketch plane is XZ (with Z inverted), extruded along +Y
# In CadQuery, we can sketch on the XZ plane and extrude in the +Y direction
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
