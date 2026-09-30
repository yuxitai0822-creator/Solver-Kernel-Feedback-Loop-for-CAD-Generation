import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\108851_4d515b10_0007\neg_02"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Build the extruded rectangle
# Dimensions from design plan (unit conversion cm->mm already applied in plan):
# length_u = 279.4 mm, width_v = 50.8 mm, extrude_distance = 19.05 mm
# Frame: u_dir = [1,0,0] (X), v_dir = [0,0,-1] (-Z), w_dir = [0,1,0] (Y)
# Origin convention: bbox_min_corner

result = (
    cq.Workplane("XZ")
    .rect(279.4, 50.8)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)