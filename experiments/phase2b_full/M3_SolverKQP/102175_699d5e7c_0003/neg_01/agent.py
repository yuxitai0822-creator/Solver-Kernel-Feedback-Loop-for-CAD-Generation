import cadquery as cq

# Create a rectangular prism based on the design plan
# Dimensions: length_u = 39.0 mm, width_v = 68.0 mm, extrude_distance = 10.0 mm
# The profile is a rectangle with corners at uv coordinates:
#   (-3.9, 6.8), (0.0, 6.8), (0.0, 0.0), (-3.9, 0.0)
# Note: The uv coordinates are in cm (from compiler notes: cm_to_mm x10)
# So we multiply by 10 to convert to mm: 
#   (-39.0, 68.0), (0.0, 68.0), (0.0, 0.0), (-39.0, 0.0)
# This gives a rectangle of width 39.0 mm and height 68.0 mm

# Build the rectangle profile
result = (cq.Workplane("XY")
          .moveTo(-39.0, 68.0)
          .lineTo(0.0, 68.0)
          .lineTo(0.0, 0.0)
          .lineTo(-39.0, 0.0)
          .close()
          .extrude(10.0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102175_699d5e7c_0003\\neg_01/generated.step")