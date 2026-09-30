import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\102525_06a3094b_0004\ex2/generated.step"

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# Build the rectangular prism
# Dimensions: length_u = 8.5 mm, width_v = 18.0 mm, extrude_distance = 2.5 mm
# Origin at bbox_min_corner, extrusion along +Y (w_dir)
result = (
    cq.Workplane("XZ")
    .rect(8.5, 18.0)
    .extrude(2.5)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
