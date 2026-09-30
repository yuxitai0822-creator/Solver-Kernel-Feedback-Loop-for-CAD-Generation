import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm, Width (v): 19.05 mm, Height (w): 12.7 mm
# The profile is a rectangle in the uv-plane, extruded along the w-direction.

# Define the rectangle profile dimensions
length_u = 95.25  # mm
width_v = 19.05   # mm
extrude_distance = 12.7  # mm

# Build the part: create a rectangle, then extrude it
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108851_4d515b10_0006\\ex2/generated.step")
