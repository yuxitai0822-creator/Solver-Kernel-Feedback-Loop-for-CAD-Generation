import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle 171.45 x 38.1 x 6.35 mm
# Perturbation: extrude depth = 9.525 mm (0.9525 cm converted to mm)

# Build the rectangle profile on the XZ plane
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So sketch on XZ plane, extrude in +Y direction

result = (
    cq.Workplane("XZ")
    .rect(171.45, 38.1, centered=True)
    .extrude(9.525)  # perturbed depth: 0.9525 cm = 9.525 mm
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108850_0dcd5ef1_0002\neg_01\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)