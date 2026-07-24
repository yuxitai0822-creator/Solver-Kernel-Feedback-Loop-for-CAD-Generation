import cadquery as cq

# Design Plan: rectangular prism with dimensions 12mm x 60mm x 40mm
# The profile is a rectangle in the UV plane (U=12mm, V=60mm)
# Extrude along W direction by 40mm

# Create the rectangular profile
result = (cq.Workplane("XY")
          .rect(12.0, 60.0)  # width=12mm (U), height=60mm (V)
          .extrude(40.0)     # extrude 40mm along Z (W direction)
         )

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\105278_909f3813_0000\\neg_01/generated.step")
