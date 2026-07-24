import cadquery as cq

# Design Plan: Washer (2)
# Dimensions: outer radius = 3.49 mm, inner radius = 2.0 mm, thickness = 0.36 mm

# Create the outer circle (radius 3.49)
outer_circle = cq.Workplane("XY").circle(3.49)

# Create the inner circle (radius 2.0) as a hole
result = (
    cq.Workplane("XY")
    .circle(3.49)  # outer boundary
    .circle(2.0)   # inner hole
    .extrude(0.36) # extrude to thickness
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\107055_0500fdd1_0027\neg_02/generated.step")
