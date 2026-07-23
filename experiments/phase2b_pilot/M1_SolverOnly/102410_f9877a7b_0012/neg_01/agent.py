import cadquery as cq

# Build an extruded annulus (bearing-like part)
# Outer radius: 6.0 mm, Inner radius: 4.25 mm, Extrude distance: 12.0 mm
# Origin convention: bbox_min_corner, so we shift the annulus center to (outer_radius, outer_radius)
# to ensure the bounding box starts at (0, 0, 0)

outer_r = 6.0
inner_r = 4.25
height = 12.0

result = (
    cq.Workplane("XY")
    .center(outer_r, outer_r)
    .circle(outer_r)
    .circle(inner_r)
    .extrude(height)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\102410_f9877a7b_0012\neg_01/generated.step"

cq.exporters.export(result, OUT_STEP_PATH)