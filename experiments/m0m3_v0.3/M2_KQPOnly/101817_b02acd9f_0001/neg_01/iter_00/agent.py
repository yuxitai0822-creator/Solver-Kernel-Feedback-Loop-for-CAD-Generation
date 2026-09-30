import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0001\neg_01\iter_00\generated.step"

# Design parameters from the design plan (in mm)
# Outer rectangle: from (-4.0, 4.0) to (0.0, 0.0) in UV space, but scaled by 10x (cm->mm conversion)
# Actually the design plan says unit is mm, and the coordinates are already in mm.
# The outer rectangle corners: (-4, 4), (0, 4), (0, 0), (-4, 0) -> width=4, height=4
# But the dimensions say outer_length_u=40.0, outer_width_v=40.0, so there's a 10x scaling.
# The design plan says unit_conversion_applied: cm_to_mm (x10), so the UV coordinates are in cm.
# So we need to multiply all UV coordinates by 10 to get mm.

SCALE = 10.0  # cm to mm

# Outer rectangle in mm (scaled from cm)
outer_pts = [
    (-4.0 * SCALE, 4.0 * SCALE),
    (0.0 * SCALE, 4.0 * SCALE),
    (0.0 * SCALE, 0.0 * SCALE),
    (-4.0 * SCALE, 0.0 * SCALE)
]

# Inner rectangle in mm (scaled from cm)
inner_pts = [
    (-0.12 * SCALE, 3.88 * SCALE),
    (-0.12 * SCALE, 0.12 * SCALE),
    (-3.88 * SCALE, 0.12 * SCALE),
    (-3.88 * SCALE, 3.88 * SCALE)
]

# Extrude distance: 520.0 mm (from design plan, explicit dimension)
extrude_distance = 520.0

# Build the profile on the XY plane
# The profile is a rectangular frame: outer rectangle with inner rectangle cut out

# Start with the outer rectangle
result = (cq.Workplane("XY")
          .moveTo(outer_pts[0][0], outer_pts[0][1])
          .lineTo(outer_pts[1][0], outer_pts[1][1])
          .lineTo(outer_pts[2][0], outer_pts[2][1])
          .lineTo(outer_pts[3][0], outer_pts[3][1])
          .close()
          .extrude(extrude_distance))

# Cut out the inner rectangle
inner_wire = (cq.Workplane("XY")
              .moveTo(inner_pts[0][0], inner_pts[0][1])
              .lineTo(inner_pts[1][0], inner_pts[1][1])
              .lineTo(inner_pts[2][0], inner_pts[2][1])
              .lineTo(inner_pts[3][0], inner_pts[3][1])
              .close())

# Extrude the inner wire to create a cutting prism
# The cutting prism must extend through the entire body
cut_prism = inner_wire.extrude(extrude_distance * 1.5)

# Perform the cut
result = result.cut(cut_prism)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
