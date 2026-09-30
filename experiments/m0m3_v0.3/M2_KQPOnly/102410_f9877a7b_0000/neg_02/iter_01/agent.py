import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102410_f9877a7b_0000\neg_02\iter_01/generated.step"

# Design Plan: extruded annulus
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 11.5 mm
# Workplane: XZ (since normal is [0,1,0] and frame u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0])
# The annulus is centered at (0,0) on the workplane.

# Build the outer circle
result = (
    cq.Workplane("XZ")
    .circle(6.0)  # outer radius
    .extrude(11.5)  # extrude along +Y (normal of XZ plane)
)

# Cut the inner hole
inner = (
    cq.Workplane("XZ")
    .circle(4.25)  # inner radius
    .extrude(11.5)
)

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)