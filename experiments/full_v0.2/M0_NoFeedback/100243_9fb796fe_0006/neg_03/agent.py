import cadquery as cq

# Create a rectangular profile based on the design plan
# The profile is a rectangle with dimensions 19.0 mm x 19.0 mm
# The rectangle is centered at the origin in the XY plane
# The extrude direction is along the Z axis (positive direction)
# Extrude distance is 130.0 mm

# Define the rectangle dimensions
length_u = 19.0  # along X axis
width_v = 19.0   # along Y axis
extrude_distance = 130.0  # along Z axis

# Create the rectangular profile
# The profile is centered at the origin
result = (cq.Workplane("XY")
          .rect(length_u, width_v)
          .extrude(extrude_distance))

# Export the result to STEP file
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\100243_9fb796fe_0006\\neg_03/generated.step")
