import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\104453_aba0f2d1_0006\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

os.makedirs(OUT_DIR, exist_ok=True)

# Outer rectangle: 50 x 30 (in mm, representing 500mm x 300mm scaled by 10)
outer_rect = cq.Workplane("XY").rect(50, 30)

# Inner rectangle: 40 x 20 (in mm, representing 400mm x 200mm scaled by 10)
inner_rect = cq.Workplane("XY").rect(40, 20)

# Create the rectangular frame profile by subtracting inner from outer
frame_profile = outer_rect.cut(inner_rect)

# Extrude the frame profile by 500 mm in the +Z direction
result = frame_profile.extrude(500)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)
