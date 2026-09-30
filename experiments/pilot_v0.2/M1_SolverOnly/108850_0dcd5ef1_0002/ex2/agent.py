import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\108850_0dcd5ef1_0002\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Dimensions in mm (converted from cm)
length_u = 171.45  # along X
width_v = 38.1     # along Z (v_dir is -Z, so we extrude along Y)
extrude_w = 6.35   # along Y (w_dir)

# Build the extruded rectangle
# The profile lies in the XZ plane (u=X, v=-Z), extruded along Y (w)
# Using rect(length_u, width_v) on the XZ plane, centered for convenience,
# then extruding along +Y.
result = (cq.Workplane("XZ")
          .rect(length_u, width_v)
          .extrude(extrude_w))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
