import cadquery as cq

# Create a rectangular plate with dimensions from design plan
# Length (u direction) = 2438.4 mm, Width (v direction) = 1219.2 mm, Thickness (w direction) = 12.7 mm
# The rectangle is centered at origin with corners at (±121.92, ±60.96) in UV space
# Note: The design plan uses UV coordinates that are 1/10 of actual dimensions (cm to mm conversion factor of 10)
# Actual dimensions: 2438.4 mm x 1219.2 mm x 12.7 mm

# Create the rectangle profile centered at origin
result = (cq.Workplane("XY")
          .rect(2438.4, 1219.2)
          .extrude(12.7))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108412_8de2f9c3_0000\\ex2/generated.step")
