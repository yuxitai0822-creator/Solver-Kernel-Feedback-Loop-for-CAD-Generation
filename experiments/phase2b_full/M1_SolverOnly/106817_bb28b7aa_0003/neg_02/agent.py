import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the center_uv is in sketch plane)
#   extrude distance = 12.192 mm
# The profile center_uv is (50.800002, 63.500002) but in part-local frame we place the circle at origin.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# We'll create a circle on the XY plane (cq.Workplane("XY")) and extrude along Z (which corresponds to w_dir).
# However, to match the frame orientation, we can rotate the workplane.
# Simpler: create a circle on the XY plane, extrude along Z, then rotate the result to align with the frame.
# But the design plan expects a disk with span_u = 9.4234, span_v = 9.4234, span_w = 12.192.
# Using XY plane and extrude along Z gives a disk with diameter 2*radius = 9.4234, height = 12.192.
# The frame's v_dir is (0,0,-1) which is opposite to Z, but span is absolute, so orientation doesn't matter for dimensions.
# We'll just create the disk centered at origin.

radius = 4.7117
height = 12.192

result = (cq.Workplane("XY")
          .circle(radius)
          .extrude(height)
         )

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106817_bb28b7aa_0003\\neg_02/generated.step")
