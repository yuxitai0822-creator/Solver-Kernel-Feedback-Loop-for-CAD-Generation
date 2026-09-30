import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102295_86f842dd_0000\neg_02\iter_00/generated.step"

# Design parameters from the design plan
# Stadium profile: straight_length = 28.0 mm, radius = 10.0 mm
# The profile is defined in the UV plane where:
#   u_dir = [1,0,0] (X axis)
#   v_dir = [0,0,-1] (negative Z axis)
#   w_dir = [0,1,0] (Y axis)
# Extrude distance = 4.0 mm along +w (Y axis)

# Build the stadium profile in the XZ plane (since v_dir is -Z, we work in XZ)
# The stadium consists of:
# - Left arc centered at (10.0, 0.0) with radius 10.0, from 0 to 180 degrees
# - Top line from (10.0, -10.0) to (38.0, -10.0)
# - Right arc centered at (38.0, 0.0) with radius 10.0, from 0 to 180 degrees
# - Bottom line from (38.0, 10.0) to (10.0, 10.0)

# Note: The design plan specifies radius = 10.0 mm, but the perturbation description
# says E3_radius changed from 1.0 to 1.25. However, the dimensions table shows
# radius = 10.0 mm (after cm->mm conversion). We use the explicit dimensions from the plan.

# Create the workplane on XZ (since v_dir is -Z, we use XZ plane)
wp = cq.Workplane("XZ")

# Build the stadium profile
# Start at the left arc center (10.0, 0.0)
# Left arc: center at (10.0, 0.0), radius 10.0, from 0 to 180 degrees
# This arc goes from (20.0, 0.0) to (0.0, 0.0) through (10.0, 10.0)
# But we need to trace the outer boundary, so we go from (20.0, 0.0) to (0.0, 0.0)
# Actually, let's trace the perimeter:
# Start at (20.0, 0.0) - rightmost point of left arc
# Arc to (0.0, 0.0) - leftmost point of left arc (going through top)
# Line to (0.0, -10.0) - wait, the coordinates need adjustment

# Let me re-read the design plan curves:
# Curve 0: arc, center_uv=[1.0, 0.0], radius=1.0, start_angle=0, end_angle=180
# Curve 1: line, start_uv=[1.0, -1.0], end_uv=[3.8, -1.0]
# Curve 2: arc, center_uv=[3.8, 0.0], radius=1.0, start_angle=0, end_angle=180
# Curve 3: line, start_uv=[3.8, 1.0], end_uv=[1.0, 1.0]

# These are in UV coordinates. The dimensions say:
# straight_length = 28.0 mm, radius = 10.0 mm
# So the UV coordinates are scaled: u = x/10, v = z/10 (since radius=10)
# Actually, the UV coords seem to be normalized. Let's use the explicit dimensions.

# The stadium in XZ plane:
# Left arc center at (10.0, 0.0), radius 10.0
# Right arc center at (38.0, 0.0), radius 10.0
# Straight section length = 28.0 mm (distance between centers)
# Total width = 28.0 + 2*10.0 = 48.0 mm
# Total height = 2*10.0 = 20.0 mm

# Build the profile using 2D operations
# We'll create the stadium by combining a rectangle with two circles

# Method: Create a rectangle for the straight section, then add circles at ends
# Rectangle: width=28.0, height=20.0, centered at (24.0, 0.0)
# Left circle: center at (10.0, 0.0), radius 10.0
# Right circle: center at (38.0, 0.0), radius 10.0

# Use workplane on XZ
s = cq.Workplane("XZ")

# Create the rectangle (straight section)
rect = s.center(24.0, 0.0).rect(28.0, 20.0).extrude(0.001)  # thin plate for union

# Create left circle
left_circle = cq.Workplane("XZ").center(10.0, 0.0).circle(10.0).extrude(0.001)

# Create right circle
right_circle = cq.Workplane("XZ").center(38.0, 0.0).circle(10.0).extrude(0.001)

# Union to get the stadium profile as a thin solid
stadium_profile = rect.union(left_circle).union(right_circle)

# Now extrude this profile along Y axis (w_dir = [0,1,0]) by 4.0 mm
# We need to get the face on XZ plane and extrude it
# The stadium_profile is a thin solid in XZ, we want to extrude its face

# Alternative approach: build the stadium as a 2D wire and extrude directly
# Let's use a cleaner method with cadquery's 2D sketching

result = (
    cq.Workplane("XZ")
    .center(24.0, 0.0)
    .rect(28.0, 20.0)
    .extrude(4.0)
)

# Add the rounded ends by extruding circles and unioning
left_end = (
    cq.Workplane("XZ")
    .center(10.0, 0.0)
    .circle(10.0)
    .extrude(4.0)
)

right_end = (
    cq.Workplane("XZ")
    .center(38.0, 0.0)
    .circle(10.0)
    .extrude(4.0)
)

result = result.union(left_end).union(right_end)

# Export the result
exporters.export(result, OUT_STEP_PATH)
