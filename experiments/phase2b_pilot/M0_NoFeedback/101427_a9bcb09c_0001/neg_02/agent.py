import cadquery as cq
import os

OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\101427_a9bcb09c_0001\neg_02'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')

os.makedirs(OUT_DIR, exist_ok=True)

# Outer rectangle dimensions (from outer ring UV coordinates)
outer_u = 198.0  # 195.5 - (-2.5)
outer_v = 60.0   # 57.5 - (-2.5)

# Inner rectangle dimensions (from inner ring UV coordinates)
inner_u = 193.0  # 193.0 - 0.0
inner_v = 55.0   # 55.0 - 0.0

# Extrusion distance
extrude_d = 25.0

# Build the rectangular frame by subtracting the inner box from the outer box
result = (
    cq.Workplane("XY")
    .rect(outer_u, outer_v)
    .extrude(extrude_d)
    .cut(
        cq.Workplane("XY")
        .rect(inner_u, inner_v)
        .extrude(extrude_d)
    )
)

# Export to STEP file
cq.exporters.export(result, OUT_STEP_PATH)
