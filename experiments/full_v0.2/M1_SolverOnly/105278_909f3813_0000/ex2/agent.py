import cadquery as cq

# Create a rectangular prism with dimensions: length_u=12mm, width_v=60mm, extrude_distance=40mm
# The profile is a rectangle centered at origin in the XY plane, extruded along Z

# Create the rectangle profile (centered at origin)
result = (
    cq.Workplane("XY")
    .rect(12.0, 60.0)  # length_u=12mm along X, width_v=60mm along Y
    .extrude(40.0)      # extrude 40mm along Z (positive direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\105278_909f3813_0000\\ex2/generated.step")
