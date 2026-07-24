import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 101.6 mm, Width (v): 101.6 mm, Height (w): 38.1 mm
# The profile is centered at origin in the uv-plane, extruded in +w direction.

# Define the rectangle profile centered at origin
# Half-length = 101.6 / 2 = 50.8, half-width = 101.6 / 2 = 50.8
# But the design plan specifies start_uv and end_uv coordinates as +/-5.079999999999999
# which is 5.08 (likely 5.08 cm converted to mm = 50.8 mm).
# So the rectangle spans from (-50.8, -50.8) to (50.8, 50.8) in uv-plane.

result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6, centered=True)  # rectangle centered at origin
    .extrude(38.1)  # extrude in +Z direction (which is +w)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103481_b27a1cdf_0010\\neg_01/generated.step")
