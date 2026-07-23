import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-SolverKernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\108850_0dcd5ef1_0002\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters (converted from cm to mm as per compiler_notes)
length_u = 171.45  # mm
width_v = 38.1     # mm
extrude_distance = 6.35  # mm

# Build the extruded rectangle
# The frame defines u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# In CadQuery's default XY plane, X aligns with u_dir and Y aligns with -v_dir
# So the rectangle dimensions map directly to length_u along X and width_v along Y
result = cq.Workplane("XY").rect(length_u, width_v).extrude(extrude_distance)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
