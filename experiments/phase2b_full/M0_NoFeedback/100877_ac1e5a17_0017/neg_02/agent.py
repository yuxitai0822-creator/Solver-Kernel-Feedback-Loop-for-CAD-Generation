import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 254.0 mm, Width (v) = 190.5 mm, Extrude distance (w) = 3.175 mm
# Note: The design plan profiles show coordinates in uv space that are 1/10 of the actual dimensions
# because a cm_to_mm (x10) conversion was applied. The actual dimensions are:
# length_u = 254.0 mm, width_v = 190.5 mm, extrude_distance = 3.175 mm

# Create the rectangle profile
result = (cq.Workplane("XY")
          .rect(254.0, 190.5)
          .extrude(3.175))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\100877_ac1e5a17_0017\\neg_02/generated.step")
