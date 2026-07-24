import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is defined in UV coordinates with origin at (-3.9, 0.0) and extends to (0.0, 6.8)
# This corresponds to a rectangle of size 3.9 x 6.8 in UV space, but the dimensions indicate 39.0 x 68.0 mm
# The UV coordinates are scaled by 10 (cm to mm conversion factor)

# Build the rectangle profile
result = (cq.Workplane("XY")
          .rect(39.0, 68.0, centered=False)
          .extrude(10.0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102175_699d5e7c_0003\\neg_01/generated.step")