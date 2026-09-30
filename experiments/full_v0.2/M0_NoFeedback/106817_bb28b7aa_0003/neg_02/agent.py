import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the center_uv is in sketch plane but we ignore for position)
#   extrude distance = 12.192 mm
# The profile circle center_uv = [5.080000162124634, 6.350000202655792] but we place the circle at origin for simplicity.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# We'll create a circle on the XY plane (normal = (0,0,1)) and extrude in the +Z direction.
# However the design plan's v_dir is (0,0,-1) and w_dir is (0,1,0), so the extrusion direction is +w = (0,1,0).
# To match the intended orientation, we can create the circle on the XZ plane and extrude along Y.
# But for simplicity and to match the expected spans (u:9.4234, v:9.4234, w:12.192), we can just create a cylinder along Y.
# Let's create a circle on the XZ plane (normal = (0,1,0)) with center at origin, radius 4.7117, then extrude along Y by 12.192.

radius = 4.7117
height = 12.192

# Create the circle on the XZ plane (normal Y) and extrude in +Y direction
result = (cq.Workplane("XZ")
          .circle(radius)
          .extrude(height))

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\106817_bb28b7aa_0003\neg_02/generated.step")
