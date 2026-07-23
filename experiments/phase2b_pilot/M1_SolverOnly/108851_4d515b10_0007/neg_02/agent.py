import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\108851_4d515b10_0007\neg_02"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

# Dimensions in mm (converted from cm)
length_u = 279.4
width_v = 50.8
extrude_w = 19.05

# Build the extruded rectangle
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the sketch plane is XZ with v pointing down (-Z), and extrusion is along +Y
# In CadQuery, we can sketch on the XZ plane and extrude along +Y
result = (cq.Workplane("XZ")
          .rect(length_u, width_v)
          .extrude(extrude_w))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
