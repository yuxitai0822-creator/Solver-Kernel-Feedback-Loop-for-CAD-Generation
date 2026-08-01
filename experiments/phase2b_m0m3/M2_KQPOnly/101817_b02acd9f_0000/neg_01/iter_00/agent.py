import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame
# Outer rectangle: u from 6.0 to 10.0, v from -7.0 to -3.0 (in UV frame)
# Inner rectangle: u from 6.12 to 9.88, v from -6.88 to -3.12
# Extrude along w direction (0,1,0) by 780.0 mm
# Note: UV coordinates are in the XZ plane (u->x, v->z), extrude along y

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0000\neg_01\iter_00/generated.step"

# Build the outer rectangle (10x4 mm in UV space, but scaled by 10 from cm->mm conversion?)
# The design plan values are in mm after conversion: outer u span = 40mm, outer v span = 40mm
# But the UV coordinates given are: u from 6 to 10 (span 4), v from -7 to -3 (span 4)
# This suggests the UV coordinates are in cm (4cm = 40mm). So we scale by 10.
# Actually, the compiler note says cm_to_mm (x10) was applied.
# The UV coordinates in the design plan are already in mm? Let's check:
# Outer: u from 10 to 6 -> span 4, v from -7 to -3 -> span 4. If these are mm, outer is 4x4 mm, not 40x40.
# But dimensions say outer_length_u = 40mm, outer_width_v = 40mm.
# So the UV coordinates must be in cm (4cm = 40mm). We'll scale by 10.

# Actually, re-reading: the design plan says unit is mm, but the compiler note says cm_to_mm (x10).
# The UV coordinates are likely in the original cm units. We'll multiply by 10 to get mm.

scale = 10.0  # cm to mm

# Outer rectangle in UV (cm) -> scaled to mm
outer_u_min = 6.0 * scale
outer_u_max = 10.0 * scale
outer_v_min = -7.0 * scale
outer_v_max = -3.0 * scale

# Inner rectangle in UV (cm) -> scaled to mm
inner_u_min = 6.12 * scale
inner_u_max = 9.88 * scale
inner_v_min = -6.88 * scale
inner_v_max = -3.12 * scale

# Extrude distance: 780.0 mm (already in mm)
extrude_dist = 780.0

# Build the profile on the XZ plane (u->x, v->z), extrude along Y (w direction = (0,1,0))
# The frame axes: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# So u maps to x, v maps to -z, w maps to y

# Create workplane on XZ (front view in cadquery)
wp = cq.Workplane("XZ")

# Build outer rectangle
# Note: v_dir is (0,0,-1), so v coordinate maps to -z. We'll negate v when placing.
outer = wp.moveTo(outer_u_min, -outer_v_min) \
           .rect(outer_u_max - outer_u_min, outer_v_max - outer_v_min, centered=False)

# Extrude outer
result = outer.extrude(extrude_dist)

# Build inner rectangle for cutting
# We need to create a separate workplane for the cut profile
cut_wp = cq.Workplane("XZ")
inner = cut_wp.moveTo(inner_u_min, -inner_v_min) \
              .rect(inner_u_max - inner_u_min, inner_v_max - inner_v_min, centered=False)

# Extrude the inner profile to create a cutting prism (overshoot to ensure clean cut)
cut_prism = inner.extrude(extrude_dist * 1.5)

# Cut the inner hole
result = result.cut(cut_prism)

# Export
importers.export(result, OUT_STEP_PATH)
