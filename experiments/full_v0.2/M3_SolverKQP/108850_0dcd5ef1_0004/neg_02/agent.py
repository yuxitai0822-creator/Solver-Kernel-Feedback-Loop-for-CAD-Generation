import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u direction) = 171.45 mm, Width (v direction) = 110.998 mm, Thickness (w direction) = 6.35 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle is in the X-Z plane (using u and v), extruded along Y (w direction)

# Create the rectangle profile in the X-Z plane
# The profile vertices in UV coordinates: (0,0), (17.145,0), (17.145,11.0998), (0,11.0998)
# Note: the design plan dimensions are 171.45 and 110.998, but the UV coordinates show 17.145 and 11.0998
# This is because a cm_to_mm (x10) conversion was applied - the original was in cm
# So 17.145 cm = 171.45 mm, and 11.0998 cm = 110.998 mm

# Build the plate
result = (
    cq.Workplane("XZ")
    .rect(171.45, 110.998, centered=False)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108850_0dcd5ef1_0004\\neg_02/generated.step")
