import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\108851_4d515b10_0009\neg_03"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
# Profile rectangle in UV plane: u_span = 209.55, v_span = 57.912
# Extrude along +w direction by 19.05mm

# In CadQuery's default XY plane, X maps to u and Y maps to v.
# Since v_dir is (0,0,-1), the Y axis in the sketch corresponds to -Z in 3D.
# We draw the rectangle with length 209.55 (along X) and width 57.912 (along Y).
# Extruding along +w (which is +Y in 3D) by 19.05mm correctly builds the part.

result = (
    cq.Workplane("XY")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export the result to STEP
cq.exporters.export(result, OUT_STEP_PATH)
