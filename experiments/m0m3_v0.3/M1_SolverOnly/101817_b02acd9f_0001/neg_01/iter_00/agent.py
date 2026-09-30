import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0001\neg_01\iter_00/generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion x10):
# Outer rectangle: 40 x 40 mm (from -4.0 to 0.0 in u, 0.0 to 4.0 in v, scaled by 10)
# Inner rectangle: 37.6 x 37.6 mm (from -3.88 to -0.12 in u, 0.12 to 3.88 in v, scaled by 10)
# Extrude distance: 520.0 mm (original 52.0 cm * 10)

# The design plan specifies:
# - Outer ring: points at (-4,4), (0,4), (0,0), (-4,0) in uv coordinates
# - Inner ring: points at (-0.12, 3.88), (-0.12, 0.12), (-3.88, 0.12), (-3.88, 3.88)
# - Extrude: 520.0 mm in +w direction

# Scale factor from design plan uv to mm: multiply by 10 (since dimensions are 40mm and 37.6mm)
scale = 10.0

# Outer rectangle corners (in mm)
outer_pts = [
    (-4.0 * scale, 4.0 * scale),   # (-40, 40)
    (0.0 * scale, 4.0 * scale),    # (0, 40)
    (0.0 * scale, 0.0 * scale),    # (0, 0)
    (-4.0 * scale, 0.0 * scale)    # (-40, 0)
]

# Inner rectangle corners (in mm)
inner_pts = [
    (-0.12 * scale, 3.88 * scale),   # (-1.2, 38.8)
    (-0.12 * scale, 0.12 * scale),   # (-1.2, 1.2)
    (-3.88 * scale, 0.12 * scale),   # (-38.8, 1.2)
    (-3.88 * scale, 3.88 * scale)    # (-38.8, 38.8)
]

extrude_distance = 520.0  # mm

# Build the part
result = (
    cq.Workplane("XY")
    .moveTo(outer_pts[0][0], outer_pts[0][1])
    .lineTo(outer_pts[1][0], outer_pts[1][1])
    .lineTo(outer_pts[2][0], outer_pts[2][1])
    .lineTo(outer_pts[3][0], outer_pts[3][1])
    .close()
    .extrude(extrude_distance)
)

# Cut the inner hole
inner_wire = (
    cq.Workplane("XY")
    .moveTo(inner_pts[0][0], inner_pts[0][1])
    .lineTo(inner_pts[1][0], inner_pts[1][1])
    .lineTo(inner_pts[2][0], inner_pts[2][1])
    .lineTo(inner_pts[3][0], inner_pts[3][1])
    .close()
    .extrude(extrude_distance * 1.5)  # overshoot to ensure clean cut
)

result = result.cut(inner_wire)

exporters.export(result, OUT_STEP_PATH)
