import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions: radius = 0.8 mm, extrude distance = 4.0 mm
# Note: The design plan uses a local coordinate system with w_dir = [0,1,0] as extrusion direction.
# We create a circle on the XY plane and extrude along the positive Z axis (which corresponds to w_dir).

# Create the disk
result = (
    cq.Workplane("XY")
    .circle(0.8)  # radius in mm
    .extrude(4.0)  # extrude distance in mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102760_26430589_0037\\neg_03/generated.step")
