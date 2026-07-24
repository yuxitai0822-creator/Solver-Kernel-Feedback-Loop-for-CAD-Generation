import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm, Width (v): 19.05 mm, Extrude (w): 12.7 mm
# The profile is a rectangle in the uv-plane, extruded in the +w direction.

# Define the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(95.25, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0006\\neg_02/generated.step")
