import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 193.0 mm, width_v = 55.0 mm, extrude_distance = 50.0 mm
# Note: The design plan dimensions are given in mm (converted from cm by factor 10).
# The profile rectangle is defined in UV space with u along x, v along z (negative direction).
# The extrude direction is +w which corresponds to +y.

# Create the rectangle profile on the XY plane (since w_dir = (0,1,0) is the extrude direction)
# The profile lies in the plane where w=0, i.e., the XY plane.
# The rectangle corners in UV: (0,55), (0,0), (193,0), (193,55)
# Map: u -> x, v -> -z (because v_dir = (0,0,-1))
# So points: (0, 0, -55), (0, 0, 0), (193, 0, 0), (193, 0, -55)

result = (
    cq.Workplane("XY")
    .moveTo(0, -55)  # start at (0, -55) in XY plane (z=0)
    .lineTo(0, 0)    # to (0, 0)
    .lineTo(193, 0)  # to (193, 0)
    .lineTo(193, -55) # to (193, -55)
    .close()
    .extrude(50.0)   # extrude along +Z (which is +w direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101427_a9bcb09c_0002\\neg_03/generated.step")
