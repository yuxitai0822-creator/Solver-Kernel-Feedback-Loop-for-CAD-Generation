import cadquery as cq

# Create the base plate profile
# The profile consists of a rectangle with a circular cutout
# From the design plan, the outer profile is defined by:
# - A vertical line from (0.9188, 1.7937) to (0.9188, 0.0)
# - A horizontal line from (0.9188, 0.0) to (3.8000, 0.0)
# - A vertical line from (3.7174, 1.7937) to (3.7174, 0.0)
# - A circular arc centered at (2.3181, 1.7491) with radius 1.4
# The inner cutout is a circle centered at (2.3181, 1.7491) with radius 1.25

# Note: The coordinates in the design plan are in cm (converted to mm by factor 10)
# But the plan says unit_conversion_applied: cm_to_mm (x10), so the values are already in mm

# Build the outer profile using a workplane
result = (
    cq.Workplane("XY")
    .moveTo(0.9188335453558412, 1.7936743887554851)
    .lineTo(0.9188335453558412, 0.0)
    .lineTo(3.8000000566244125, 0.0)
    .lineTo(3.7174115708793822, 0.0)  # This line seems redundant but follows the plan
    .lineTo(3.7174115708793822, 1.7936743887554851)
    # Close the profile with a circular arc
    .threePointArc(
        (2.3181225581176115, 1.7490620724718653 + 1.4),  # approximate point on arc
        (0.9188335453558412, 1.7936743887554851)
    )
    .close()
    .extrude(18.0)
)

# Now cut out the inner circle
result = (
    result
    .faces(">Z")
    .workplane()
    .circle(1.2500000000000002)
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104283_e5646f96_0001\\neg_01/generated.step")
