import cadquery as cq
import math

# Stadium parameters from design plan
# The plan specifies a unit conversion of cm_to_mm (x10) was applied.
# Profile curves (in local uv frame) have radius=1 and straight length=2.8.
# Dimensions section specifies radius=10 and straight_length=28, confirming the x10 scale.
radius = 10.0
straight_length = 28.0
extrude_distance = 4.0

# The local frame maps u -> X, v -> -Z, w -> Y.
# In the XZ plane (where u=X, v=-Z), the stadium is oriented horizontally.
# The straight sides of the stadium run parallel to the X axis.
# The semicircular caps are at X=10 and X=10+28=38.
# The stadium spans Z from -10 to 10 (since v=-Z, uv v=10 -> Z=-10).

# Build the stadium profile in the XZ plane
# We construct it as a rectangle with two semicircular ends.
# CadQuery's rect() is defined by width (X) and height (Z).
# Here, width is the straight_length (28), and height is 2*radius (20).
# The rect is centered at (10+14, 0) = (24, 0) in XZ.

profile_x_center = 10.0 + straight_length / 2.0  # 24.0
profile_z_center = 0.0

profile = (
    cq.Workplane("XZ")
    .center(profile_x_center, profile_z_center)
    .rect(straight_length, 2 * radius)
    .wires()
    .toPending()
)

# Add the left semicircle (at X=10, radius 10, sweeping from Z=10 down to Z=-10)
# In XZ, start angle 90 (Z=10), end angle -90 (Z=-10)
profile = profile.arc(
    (10.0 - profile_x_center, 0.0), radius, 90, -180
).wires().toPending()

# Add the right semicircle (at X=38, radius 10, sweeping from Z=-10 up to Z=10)
# In XZ, start angle -90 (Z=-10), end angle 90 (Z=10)
profile = profile.arc(
    (38.0 - profile_x_center, 0.0), radius, -90, 180
).wires().toPending()

# Extrude along +Y (which corresponds to +w in the local frame)
result = profile.extrude(extrude_distance)

# Export the result to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\102295_86f842dd_0000\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
