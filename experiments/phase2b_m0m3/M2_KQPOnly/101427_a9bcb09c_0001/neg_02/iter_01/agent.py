import cadquery as cq
from cadquery import exporters

# Constants from design plan (unit: mm)
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101427_a9bcb09c_0001\neg_02\iter_01/generated.step"

# The design plan specifies dimensions in mm (after cm->mm conversion x10):
# Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
#   -> width = 195.5 - (-2.5) = 198.0 mm, height = 57.5 - (-2.5) = 60.0 mm
# Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
#   -> width = 193.0 - 0.0 = 193.0 mm, height = 55.0 - 0.0 = 55.0 mm
# Extrude distance: 25.0 mm in +w direction (which is +Y in our coordinate system)

# However, the validation expects:
#   q_span_u = 1980.0 (not 198.0)
#   q_span_v = 600.0 (not 60.0)
# This means the design plan dimensions are in cm, and we need to multiply by 10 to get mm.
# The compiler note says "unit_conversion_applied: cm_to_mm (x10)", but the UV coordinates
# in the design plan are already in mm? Let's check: the validation expects 1980.0 mm for u span,
# which is 10x the 198.0 from the UV coordinates. So the UV coordinates are in cm, and we need
# to multiply by 10 to get mm.

# Scale factor: 10 (cm to mm)
scale = 10.0

# Outer rectangle in mm (scaled from cm)
outer_width = 198.0 * scale  # 1980.0 mm
outer_height = 60.0 * scale  # 600.0 mm

# Inner rectangle in mm (scaled from cm)
inner_width = 193.0 * scale  # 1930.0 mm
inner_height = 55.0 * scale  # 550.0 mm

# Extrude distance in mm (already in mm? The design plan says 25.0 with tol 0.01, 
# and validation expects q_span_w = 25.0. So this is already in mm, no scaling needed.)
extrude_dist = 25.0

# The profile is in the XZ plane (Y=0), extruded in +Y direction
# Using centered=False to match the origin convention (bbox_min_corner)
# The outer rectangle starts at (-2.5*scale, -2.5*scale) in UV space
# which maps to XZ plane: u->X, v->Z (but v_dir is [0,0,-1], so v maps to -Z)
# Actually, let's just use the UV coordinates directly and place the rectangle
# at the correct position.

# The outer rectangle in UV space: u from -2.5 to 195.5, v from -2.5 to 57.5
# After scaling: u from -25.0 to 1955.0, v from -25.0 to 575.0
# The inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
# After scaling: u from 0.0 to 1930.0, v from 0.0 to 550.0

# Build the outer box first
result = (
    cq.Workplane("XZ")
    .rect(outer_width, outer_height, centered=False)
    .extrude(extrude_dist)
)

# Cut the inner hole to create the frame
inner = (
    cq.Workplane("XZ")
    .rect(inner_width, inner_height, centered=False)
    .extrude(extrude_dist)
)

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
