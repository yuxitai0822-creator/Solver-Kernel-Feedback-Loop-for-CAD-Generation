import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm
# Width (v): 19.05 mm
# Height (w): 12.7 mm

# The profile is a rectangle in the uv-plane, then extruded in the +w direction.
# Based on the design plan, the rectangle spans from (0,0) to (9.524999999999999, 1.905) in uv-space.
# Note: The dimensions in the plan are given as length_u=95.25 and width_v=19.05.
# The uv coordinates in the profile curves appear to be scaled by 10 (since 9.525*10=95.25, 1.905*10=19.05).
# This is consistent with the compiler note "cm_to_mm (x10)".
# So we build the rectangle with the actual mm dimensions.

# Build the rectangle profile on the xy-plane (u=x, v=y)
result = (
    cq.Workplane("XY")
    .rect(95.25, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108851_4d515b10_0006\\neg_01/generated.step")
