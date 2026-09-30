import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\108851_4d515b10_0009\neg_03"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
# Profile rectangle in UV plane: u_span = 209.55 mm, v_span = 57.912 mm
# Extrude along +w direction (Y axis) by distance = 19.05 mm

# In CadQuery, we work on the XZ plane to match the UV plane (u=X, v=-Z).
# The rectangle is drawn with length=209.55 (along X) and width=57.912 (along Z).
# To map v_dir=(0,0,-1), we extrude in the -Z direction. 
# However, CadQuery extrudes positively along the plane normal (+Z for XZ plane).
# To extrude 19.05mm along +w (Y axis), we can simply rotate the resulting part.
# Alternatively, we can sketch on the XY plane (u=X, w=Y) and extrude along -Y to map v=(0,0,-1).
# Let's use the straightforward approach: sketch on XY, extrude 57.912 along Z (which is v_dir inverted), 
# then rotate to align Y with w_dir. 

# Actually, the simplest way to match the exact frame is:
# 1. Sketch on the XY plane. X maps to u_dir=(1,0,0). Y maps to w_dir=(0,1,0).
# 2. Draw a rectangle of 209.55 x 19.05.
# 3. Extrude 57.912 along the -Z axis to map v_dir=(0,0,-1).

result = (
    cq.Workplane("XY")
    .rect(209.55, 19.05)
    .extrude(-57.912)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
