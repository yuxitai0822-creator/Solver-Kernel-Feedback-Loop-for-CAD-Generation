import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\102525_06a3094b_0000\ex2"
os.makedirs(OUT_DIR, exist_ok=True)

OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

# Dimensions from design plan (converted from cm to mm)
length_u = 3.9  # mm
width_v = 4.9   # mm
extrude_w = 1.55 # mm

# Build the rectangular prism
# The design plan specifies origin at bbox_min_corner.
# CadQuery's rect() centers at (0,0) by default, so we offset by half dimensions.
result = (cq.Workplane("XY")
          .rect(length_u, width_v)
          .translate((length_u / 2, width_v / 2, 0))
          .extrude(extrude_w))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
