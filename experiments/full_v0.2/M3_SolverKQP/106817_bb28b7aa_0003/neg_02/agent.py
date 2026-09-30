import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the center_uv is in sketch plane)
#   extrude distance = 12.192 mm
# The profile center_uv is (50.800002, 63.500002) but that is in the sketch plane;
# we place the circle at the origin in the local frame for simplicity.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# We'll create a workplane on the XY plane (normal = (0,0,1)) and then rotate?
# Actually easier: use the standard XY plane and extrude along Z.
# The resulting disk will have diameter 2*radius = 9.4234 mm, height 12.192 mm.

radius = 4.7117
height = 12.192

result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(height)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0003\\neg_02/generated.step")
