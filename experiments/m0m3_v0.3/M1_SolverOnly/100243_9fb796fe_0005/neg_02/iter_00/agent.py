import cadquery as cq
from cadquery import exporters

# Design Plan: Drone Leg Left - square strut
# Extruded rectangle: 19mm x 19mm profile, extruded 200mm along Y axis
# Profile center at origin, rectangle aligned with XZ plane

# Create the rectangular profile (19mm x 19mm) centered at origin on XZ plane
result = (
    cq.Workplane("XZ")
    .rect(19.0, 19.0, centered=True)
    .extrude(200.0)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0005\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)