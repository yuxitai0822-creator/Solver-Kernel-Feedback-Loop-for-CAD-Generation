import cadquery as cq

# Design Plan: extruded circle (disk) with radius 3.0 mm and height 25.0 mm
# The profile is a circle of radius 0.3 (in UV space) but the actual radius is 3.0 mm.
# The extrude distance is 25.0 mm along +w (z-axis).

# Create the disk by extruding a circle
result = (
    cq.Workplane("XY")
    .circle(3.0)  # radius in mm
    .extrude(25.0)  # extrude along +z
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107467_a8afc51d_0002\\neg_03/generated.step")
