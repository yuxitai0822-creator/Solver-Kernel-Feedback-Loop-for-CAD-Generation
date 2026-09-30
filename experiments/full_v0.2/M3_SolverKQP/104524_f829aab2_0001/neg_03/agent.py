import cadquery as cq

# Design Plan: extruded circle (disk) with radius 7.5 mm and height 20.0 mm
# The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the extrusion is along +w = (0,1,0) direction.
# The circle is centered at (0,0) in the uv-plane, which corresponds to the xz-plane in world coordinates.
# We'll create the circle on the xz-plane and extrude along y-axis.

# Create the circle profile on the xz-plane (normal = y-axis)
result = (
    cq.Workplane("XZ")
    .circle(7.5)  # radius from design plan
    .extrude(20.0)  # extrude along y-axis (positive direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104524_f829aab2_0001\\neg_03/generated.step")
