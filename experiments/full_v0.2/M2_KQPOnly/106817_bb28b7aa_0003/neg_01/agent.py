import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the design plan shows radius 0.47117 but unit conversion cm->mm x10 gives 4.7117)
#   extrude distance = 12.192 mm
#   center_uv = (50.800002, 63.500002) but in local frame we place at origin for simplicity

# Create a circle at origin with radius 4.7117 mm
result = (
    cq.Workplane("XY")
    .circle(4.7117)
    .extrude(12.192)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106817_bb28b7aa_0003\\neg_01/generated.step")
