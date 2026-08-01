import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk)
# - Circle center: (5.080000162124634, 6.350000202655792) in UV frame
# - Circle radius: 0.4711700000000002 (in UV frame, but dimensions show 4.7117 mm radius)
# - Extrude distance: 12.192 mm (from explicit dimension)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# - Workplane: XZ (since v_dir is [0,0,-1], normal is w_dir=[0,1,0])

# The design plan specifies:
# - radius = 4.7117 mm (from dimensions.profiles[0].radius.value)
# - center_uv = [50.800002, 63.500002] (from dimensions.profiles[0].center_uv)
# - extrude_distance = 12.192 mm

# Note: The UV coordinates in the profile are [5.08, 6.35] but dimensions show [50.8, 63.5]
# The compiler note says unit conversion cm_to_mm (x10), so the profile center is in cm?
# Actually the profile center_uv is [5.08, 6.35] and dimensions center_uv is [50.8, 63.5]
# The radius in profile is 0.47117, in dimensions is 4.7117
# This suggests the profile uses cm and dimensions use mm.
# We'll use the mm values from dimensions.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0003\neg_01\iter_00\generated.step"

# Parameters from design plan (in mm)
center_x = 50.800002
center_y = 63.500002
radius = 4.7117
extrude_distance = 12.192

# Build the disk
# Workplane: XZ (since v_dir=[0,0,-1] means v is -Z, so sketch plane is XZ)
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So sketch plane normal is w_dir = [0,1,0] which is Y axis
# In cadquery, we work on XZ plane and extrude in Y direction

result = (
    cq.Workplane("XZ")
    .moveTo(center_x, center_y)
    .circle(radius)
    .extrude(extrude_distance)
)

exporters.export(result, OUT_STEP_PATH)
