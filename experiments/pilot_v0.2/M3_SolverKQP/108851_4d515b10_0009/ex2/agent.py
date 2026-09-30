import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\108851_4d515b10_0009\ex2'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')
os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters:
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in uv-plane: length_u = 209.55, width_v = 57.912
# Extrude along +w direction (Y-axis) by distance = 19.05

# In CadQuery's default XY plane, X maps to u_dir and Y maps to v_dir.
# Since v_dir is [0,0,-1] (downward in Z), the profile rectangle in the XY plane
# must have its Y-extent go from 0 to -57.912 to match the uv-coordinates.
# Extruding along +w (Y-axis) by 19.05 completes the transformation.

result = (
    cq.Workplane("XY")
    .rect(209.55, 57.912)
    .translate((0, -57.912 / 2, 0))  # Shift so Y ranges from 0 to -57.912
    .extrude(19.05)                   # Extrude along +Y (w_dir)
)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)