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
    .circle(5.5372)  # outer circle
    .circle(1.9812)  # inner circle (hole)
    .extrude(1.3208)  # extrude along Z
)

# The design plan frame has w_dir = (0,1,0) meaning the extrusion direction should be Y.
# Our current extrusion is along Z. We need to rotate the result so that Z maps to Y.
# Rotation: align (0,0,1) to (0,1,0) -> rotate -90 deg around X axis.
result = result.rotate((0,0,0), (1,0,0), -90)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\106817_bb28b7aa_0004\\neg_03/generated.step")
