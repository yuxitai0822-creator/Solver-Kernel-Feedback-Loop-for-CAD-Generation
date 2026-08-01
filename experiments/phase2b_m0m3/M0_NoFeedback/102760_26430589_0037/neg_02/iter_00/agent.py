import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\102760_26430589_0037\neg_02\iter_00\generated.step"

# Design Plan parameters:
# - Disk with radius 0.8 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance 4.0 mm (from dimensions.extrude_distance.value)
# - Circle profile radius 0.08 mm (from profiles[0].rings[0].curves[0].radius) - this is the sketch radius
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# - Extrude direction: -w (i.e., along negative Y axis)

# Build the part:
# 1. Create a circle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
# 2. Extrude along Y direction (w_dir is [0,1,0], extrude in -w = negative Y)

# The circle radius in the sketch is 0.08 mm (from the curves section)
# But the actual part radius is 0.8 mm (from dimensions section)
# The perturbation changed the sketch radius from 0.08 to 0.1
# We use the perturbed value: 0.1 mm for the sketch circle
# The extrude distance is 4.0 mm

# Create workplane on XZ plane
result = (
    cq.Workplane("XZ")
    .circle(0.1)  # perturbed radius from 0.08 to 0.1
    .extrude(4.0)  # extrude along Y (positive Y since we're on XZ plane)
)

# The extrude direction should be -w = negative Y
# Since we're on XZ plane, extrude goes in +Y by default
# To extrude in -Y, we need to negate the distance
# But the design says direction is -w, so we extrude in negative Y
# Rebuild with correct direction
result = (
    cq.Workplane("XZ")
    .circle(0.1)  # perturbed radius
    .extrude(-4.0)  # extrude in negative Y direction
)

exporters.export(result, OUT_STEP_PATH)