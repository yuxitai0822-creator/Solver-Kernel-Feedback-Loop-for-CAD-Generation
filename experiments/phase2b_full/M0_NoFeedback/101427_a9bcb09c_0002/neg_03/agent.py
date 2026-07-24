import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle of 193.0 mm x 55.0 mm (note: dimensions in plan are 1930.0 x 550.0 but curves show 193.0 x 55.0, using curves as they define the actual shape)
# Extrude by 50.0 mm in the +w direction (which maps to +Y in world coordinates)

# Create the rectangle profile on the XZ plane (since u_dir = X, v_dir = -Z, w_dir = Y)
# The rectangle corners in UV space: (0,0), (193,0), (193,55), (0,55)
# In world: u -> X, v -> -Z, so point (u,v) maps to (u, 0, -v)

result = (
    cq.Workplane("XZ")
    .center(193.0/2, -55.0/2)  # center the rectangle
    .rect(193.0, 55.0)
    .extrude(50.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101427_a9bcb09c_0002\\neg_03/generated.step")
