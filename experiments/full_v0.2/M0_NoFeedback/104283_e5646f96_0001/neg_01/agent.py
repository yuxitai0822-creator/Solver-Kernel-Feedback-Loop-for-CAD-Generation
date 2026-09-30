import cadquery as cq

# Create the base plate (outer profile)
# The outer profile is defined by two vertical lines and a circular arc at the top
# Points from the design plan (in mm, converted from cm):
# Start at (0.9188335453558412, 0.0)
# Line up to (0.9188335453558412, 1.7936743887554851)
# Arc (circle) center at (2.3181225581176115, 1.7490620724718653) radius 1.4
# Line down from (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
# Close the profile

# Build the outer profile as a wire
outer_wire = (
    cq.Workplane("XY")
    .moveTo(0.9188335453558412, 0.0)
    .lineTo(0.9188335453558412, 1.7936743887554851)
    .threePointArc(
        (2.3181225581176115, 1.7490620724718653 + 1.4),  # top of arc
        (3.7174115708793822, 1.7936743887554851)
    )
    .lineTo(3.7174115708793822, 0.0)
    .close()
    .wire()
)

# Create the inner hole (circle)
inner_center = (2.3181225581176115, 1.7490620724718653)
inner_radius = 1.2500000000000002

# Build the full profile with hole
result = (
    cq.Workplane("XY")
    .placeSketch(outer_wire)
    .circle(inner_center[0], inner_center[1], inner_radius)  # hole
    .extrude(18.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\104283_e5646f96_0001\\neg_01/generated.step")
