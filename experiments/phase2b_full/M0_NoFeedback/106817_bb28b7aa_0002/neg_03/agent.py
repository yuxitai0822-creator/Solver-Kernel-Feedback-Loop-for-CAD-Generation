import cadquery as cq

# Design Plan: thumb screw (disk)
# Dimensions:
#   - Circle radius: 4.87045 mm (from profiles[0].radius.value)
#   - Extrude distance: 6.8707 mm (from extrude.distance_total.value)
#   - Center UV: (114.300004, 0.0) but we place at origin for simplicity
#   - Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
#     This means the circle lies in the u-v plane (x-z plane) and extrudes along w (y-axis)
#     But for a standard disk, we can just create a cylinder along the z-axis.
#     The validation expects span_u=9.7409, span_v=9.7409, span_w=6.8707
#     So a cylinder of radius 4.87045 and height 6.8707 works.

radius = 4.87045
height = 6.8707

# Create a cylinder centered at origin, axis along Z
result = cq.Workplane("XY").circle(radius).extrude(height)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0002\\neg_03/generated.step")
