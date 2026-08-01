import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Body: extruded circle
# Profile: circle, radius 0.8 mm (from dimensions.profiles[0].radius.value)
# Extrude: one_side, direction -w, distance 4.0 mm (from dimensions.extrude_distance.value)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# The sketch plane is defined by u and v axes: u (x-axis) and v (z-axis negative)
# So the sketch plane is XZ (with v reversed, but that's just orientation)
# Extrude direction is -w = -[0,1,0] = [0,-1,0] (negative Y)

# Build the result
result = (
    cq.Workplane("XZ")  # sketch plane: XZ (u=x, v=z)
    .circle(0.8)  # radius from design plan
    .extrude(4.0)  # extrude distance along normal (Y direction)
)

# The extrude direction in the design plan is -w = -[0,1,0] = [0,-1,0]
# In CadQuery, Workplane("XZ") extrudes along +Y by default.
# To extrude along -Y, we need to negate the distance.
# But the design plan says distance_total = 4.0, direction = -w.
# So we should extrude -4.0 in Y direction.
# Let's rebuild with correct direction:
result = (
    cq.Workplane("XZ")
    .circle(0.8)
    .extrude(-4.0)  # negative Y direction
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102760_26430589_0037\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)