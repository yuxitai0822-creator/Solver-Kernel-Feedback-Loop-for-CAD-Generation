import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion? Wait, dimensions say 132.5 and 75.0)
# The design plan dimensions: outer_radius=132.5, inner_radius=75.0, extrude_distance=100.0
# All in mm.

# Build the annulus by extruding a washer shape
result = (
    cq.Workplane("XY")
    .circle(132.5)  # outer radius
    .circle(75.0)   # inner radius (creates a hole)
    .extrude(100.0)  # extrude along Z
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\107668_cf76b132_0001\neg_01/generated.step")
