import cadquery as cq
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104283_e5646f96_0001\neg_03\iter_02\generated.step"

# Design Plan interpretation:
# - Two profiles (outer rings) that share a common circle feature
# - Profile 1: rectangle with a circular arc on one side
# - Profile 2: rectangle with a circular arc on one side and a concentric inner circle (hole)
# - Extrude 18.0 mm in +Z direction
# - The geometry is essentially a slotted plate with a hole

# Build the base profile (Profile 1 from design plan)
# Points from the design plan curves:
# Line 1: (0.9188335453558412, 1.7936743887554851) to (0.9188335453558412, 0.0)
# Line 2: (0.9188335453558412, 0.0) to (3.8000000566244125, 0.0)
# Line 3: (3.7174115708793822, 1.7936743887554851) to (3.7174115708793822, 0.0)
# Circle: center (2.3181225581176115, 1.7490620724718653), radius 1.4

# Note: The design plan has two profiles. Profile 1 is the outer shape (rectangle + circular end)
# Profile 2 has the same outer shape plus an inner circle (hole).
# The perturbation changes the y-coordinate of the top edge from 1.7936743887554851 to 1.434939511004388

# Build using a 2D sketch approach
result = (
    cq.Workplane("XY")
    # Start with the base rectangle
    .moveTo(0.9188335453558412, 0.0)
    .lineTo(3.8000000566244125, 0.0)
    .lineTo(3.7174115708793822, 1.434939511004388)  # perturbed y-coordinate
    .lineTo(0.9188335453558412, 1.434939511004388)  # perturbed y-coordinate
    .close()
    .extrude(18.0)
)

# Now add the circular feature on top (the rounded end)
# The circle center is at (2.3181225581176115, 1.7490620724718653) with radius 1.4
# But since the top edge is now at y=1.434939511004388, we need to adjust
# The circle center y-coordinate should be adjusted relative to the perturbation
# Original center y: 1.7490620724718653
# Original top edge y: 1.7936743887554851
# Difference: 1.7490620724718653 - 1.7936743887554851 = -0.0446123162836198
# Perturbed top edge y: 1.434939511004388
# Perturbed center y: 1.434939511004388 + (-0.0446123162836198) = 1.3903271947207682

circle_center_x = 2.3181225581176115
circle_center_y = 1.3903271947207682  # adjusted for perturbation
circle_radius = 1.4

# Create the circular boss on top
result = (
    result
    .faces(">Z")
    .workplane()
    .moveTo(circle_center_x, circle_center_y)
    .circle(circle_radius)
    .extrude(18.0)  # extrude to match the full height
)

# Cut the inner hole (from Profile 2 inner ring)
# Inner circle: center (2.3181225581176115, 1.7490620724718653), radius 1.25
# Adjust center y for perturbation: 1.3903271947207682
inner_circle_radius = 1.25

result = (
    result
    .faces(">Z")
    .workplane()
    .moveTo(circle_center_x, circle_center_y)
    .circle(inner_circle_radius)
    .cutThruAll()
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
