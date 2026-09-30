import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\104453_aba0f2d1_0006\ex2/generated.step"

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# Create the outer rectangle (50 x 30 mm)
outer_rect = cq.Workplane("XY").rect(50, 30)

# Create the inner rectangle (40 x 20 mm) to form the hollow frame profile
inner_rect = cq.Workplane("XY").rect(40, 20)

# Extrude the rectangular frame profile by 500 mm along +Z
result = outer_rect.cut(inner_rect).extrude(500)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)