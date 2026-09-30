import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 254.0 mm, width_v = 190.5 mm, extrude distance = 3.175 mm
# Note: The design plan uses a local frame with u=x, v=y, w=z.
# The rectangle profile is defined in UV space with corners at (0,0), (25.4,0), (25.4,19.05), (0,19.05).
# However, the explicit dimensions state length_u = 254.0 and width_v = 190.5.
# The UV coordinates appear to be in cm (since compiler notes say cm_to_mm x10).
# So we scale the UV coordinates by 10 to get mm: 25.4*10=254, 19.05*10=190.5.
# We'll build the rectangle directly using the explicit dimensions.

# Create the rectangle profile in the XY plane (u=x, v=y)
result = (cq.Workplane("XY")
          .rect(254.0, 190.5, centered=False)
          .extrude(3.175))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100877_ac1e5a17_0017\\neg_01/generated.step")
