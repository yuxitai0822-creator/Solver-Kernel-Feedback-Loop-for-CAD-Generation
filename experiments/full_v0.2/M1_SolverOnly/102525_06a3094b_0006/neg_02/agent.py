import cadquery as cq

# Create a rectangular prism with dimensions: length_u=11.3, width_v=21.0, extrude_distance=3.0
# The profile is centered on the origin in the UV plane, then extruded in the +W direction.

# Define the rectangle dimensions
length_u = 11.3  # along X axis
width_v = 21.0   # along Z axis (since v_dir = [0,0,-1], but we'll use positive Z for simplicity)
extrude_distance = 3.0  # along Y axis (w_dir = [0,1,0])

# Build the rectangle centered at origin in the XZ plane
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102525_06a3094b_0006\\neg_02/generated.step")
