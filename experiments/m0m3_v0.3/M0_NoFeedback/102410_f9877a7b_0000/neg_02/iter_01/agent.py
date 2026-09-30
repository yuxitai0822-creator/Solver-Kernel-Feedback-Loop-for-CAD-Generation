import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102410_f9877a7b_0000\neg_02\iter_01/generated.step"

# Parameters from design plan
outer_radius = 6.0  # mm
inner_radius = 4.25  # mm
extrude_distance = 11.5  # mm

# Build the annulus using cadquery
result = (
    cq.Workplane("XZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
