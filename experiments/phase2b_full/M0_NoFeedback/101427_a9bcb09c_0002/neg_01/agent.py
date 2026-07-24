import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle of 193.0 mm x 55.0 mm (note: dimensions in plan are 1930.0 x 550.0 but unit conversion cm->mm x10 means actual mm values are 193.0 x 55.0)
# Extrude by 50.0 mm in the +w direction (which maps to +Y in world coordinates)

# Create the rectangle profile on the XZ plane (since u_dir = X, v_dir = -Z, w_dir = Y)
# The rectangle spans from (0,0) to (193, 55) in UV space
# In world coordinates: u -> X, v -> -Z, so the rectangle lies in the XZ plane
# Starting corner at (0, 0, 0) and extending to (193, 0, -55)

result = (
    cq.Workplane("XZ")
    .center(193.0/2, -55.0/2)  # center the rectangle
    .rect(193.0, 55.0)
    .extrude(50.0)  # extrude along Y (positive w direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101427_a9bcb09c_0002\\neg_01/generated.step")
