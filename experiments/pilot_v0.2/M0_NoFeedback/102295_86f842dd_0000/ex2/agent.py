import cadquery as cq
import math

# Stadium parameters (unit conversion applied: cm to mm)
# The profile curves define a stadium with radius 1.0 and straight length 2.8 in local units.
# After cm_to_mm conversion, radius = 10.0 mm, straight_length = 28.0 mm.
# Total span along u = 2*radius + straight_length = 48.0 mm.
# Total span along v = 2*radius = 20.0 mm.

radius = 10.0
straight_length = 28.0
extrude_distance = 4.0

# Build the stadium profile on the XZ plane (u=X, v=-Z, w=Y)
# The stadium center is at (radius, 0) in the local 2D frame.
# In the XZ plane, this maps to X=radius, Z=0.
# The extrusion direction +w maps to +Y.

result = (
    cq.Workplane("XZ")
    .center(radius, 0)
    .slot2D(straight_length, radius, 0)  # slot2D(length, diameter, angle)
    .extrude(extrude_distance)
)

# Export the result to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\102295_86f842dd_0000\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
