import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangular frame
# Outer rectangle: u from 6.0 to 10.0, v from -7.0 to -3.0 (in UV frame)
# Inner rectangle: u from 6.12 to 9.88, v from -6.88 to -3.12
# Extrude along w direction (0,1,0) by 780.0 mm
# Note: UV coordinates are in the XZ plane (u->x, v->z), extrude along y

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0000\neg_01\iter_01/generated.step"

# The design plan says unit is mm, but compiler note says cm_to_mm (x10) was applied.
# The UV coordinates are in cm originally. We scale by 10 to get mm.
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
cq.exporters.export(result, OUT_STEP_PATH)