import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions (in mm):
#   outer radius = 5.5372
#   inner radius = 1.9812
#   thickness (extrude distance) = 1.3208
# The profile center in UV is at (-25.400001, 12.7) but we place the sketch at origin for simplicity.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# We'll create the annulus on the XY plane (normal = (0,0,1)) and extrude along Z.
# To match the frame orientation, we can rotate the result.

# Build the washer
result = (
    cq.Workplane("XY")
    .circle(5.5372)
    .circle(1.9812)
    .extrude(1.3208)
)

# The frame in the design plan has v_dir = (0,0,-1) and w_dir = (0,1,0).
# This means the extrusion direction (w) is Y, and the profile plane normal is -Z.
# Our current result has extrusion along Z, profile on XY.
# To match: rotate 90° around X axis so that Z becomes Y.
result = result.rotate((0,0,0), (1,0,0), -90)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0004\\neg_01/generated.step")
