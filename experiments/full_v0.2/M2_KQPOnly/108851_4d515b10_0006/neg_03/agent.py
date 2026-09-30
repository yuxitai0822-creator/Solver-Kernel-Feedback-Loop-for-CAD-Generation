import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm
# Width (v): 19.05 mm
# Height (w): 12.7 mm

# The design plan specifies a rectangle in the uv-plane with corners at:
# (0, 0), (9.524999999999999, 0), (9.524999999999999, 1.905), (0, 1.905)
# Note: These values appear to be in cm (divided by 10), but the unit is mm.
# The actual dimensions from the plan are: length_u = 95.25 mm, width_v = 19.05 mm
# The extrude distance is 12.7 mm

# Build the rectangle profile and extrude
result = (
    cq.Workplane("XY")
    .rect(95.25, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\108851_4d515b10_0006\\neg_03/generated.step")
