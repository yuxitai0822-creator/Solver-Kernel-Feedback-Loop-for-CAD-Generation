import cadquery as cq

# Create a washer-like bearing part: an extruded annulus (ring)
# Outer radius = 17.5 mm, inner radius = 12.5 mm, total height = 10.0 mm (symmetric about XY plane)

# Build the outer circle
outer_circle = cq.Workplane("XY").circle(17.5)

# Build the inner circle (cutout) on the same workplane
inner_circle = cq.Workplane("XY").circle(12.5)

# Create the annulus by subtracting inner from outer, then extrude symmetrically
result = (
    cq.Workplane("XY")
    .circle(17.5)          # outer boundary
    .circle(12.5)          # inner boundary (creates a hole)
    .extrude(5.0, both=True)  # extrude 5 mm each side => total 10 mm
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\106323_77f22d29_0004\neg_03/generated.step")
