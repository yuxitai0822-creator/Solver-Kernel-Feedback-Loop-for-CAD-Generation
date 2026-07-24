import cadquery as cq

# Design Plan: extruded stadium (ArmRest v1)
# Dimensions: straight_length=500.0 mm, radius=50.0 mm, extrude_distance=100.0 mm
# Note: The plan's profiles use radius=5.0 and straight_length=50.0 in UV space,
# but the dimensions section says straight_length=500.0, radius=50.0.
# The UV curves use radius=5.0 and line length 50.0, which would give a small part.
# To match the expected spans (u=600, v=100, w=100), we scale by 10x.
# This is consistent with the compiler note "cm_to_mm (x10)".
# So we build a stadium with straight_length=500, radius=50, extrude=100.

# Build the stadium profile in the XY plane (u=x, v=y), then extrude along Z (w).
# Center the shape so that the bounding box spans are as expected.
# The stadium consists of two semicircles (radius=50) connected by two lines (length=500).
# Total width (v direction) = 2*radius = 100, total length (u direction) = 500 + 2*radius = 600.

# We'll create the profile using a workplane and then extrude.

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(-250, -50)  # start at bottom-left of the straight section
    .threePointArc((0, -100), (250, -50))  # left semicircle (center at (-250,0)? Actually easier: use two arcs)
    # Simpler: use a slot2D or build with lines and arcs.
    # Let's do a proper stadium: start at (-250, -50), line to (250, -50), arc to (250, 50), line to (-250, 50), arc to (-250, -50).
)

# Actually, let's rebuild cleanly:
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(-250, -50)
    .lineTo(250, -50)
    .threePointArc((250 + 50, 0), (250, 50))  # right semicircle (center at (250,0))
    .lineTo(-250, 50)
    .threePointArc((-250 - 50, 0), (-250, -50))  # left semicircle (center at (-250,0))
    .close()
    .extrude(100.0)
)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104453_aba0f2d1_0002\\neg_01/generated.step")
