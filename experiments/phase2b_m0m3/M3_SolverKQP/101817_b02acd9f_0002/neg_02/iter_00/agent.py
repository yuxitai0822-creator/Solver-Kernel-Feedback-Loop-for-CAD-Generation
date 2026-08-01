import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0002\neg_02\iter_00/generated.step"

# Design Plan: rectangular frame (hollow box) with outer dimensions 42.4 x 42.4 mm, inner 40.0 x 40.0 mm, extruded 1120.0 mm along w-axis (x-direction)
# The profile is in the YZ plane (u,v coordinates map to y,z).
# Outer ring: u from -6.12 to -1.88, v from 10.88 to 15.12 (in uv space, but after unit conversion cm->mm, these are multiplied by 10)
# Inner ring: u from -6.0 to -2.0, v from 11.0 to 15.0
# The extrude direction is -w (negative x), distance 1120.0 mm

# Convert uv coordinates to mm (already in mm per design plan, but the values are given as cm? Actually the plan says unit_conversion_applied: cm_to_mm (x10), so the uv values are in cm? 
# Let's check: outer dimensions are 42.4 mm, which matches 4.24 cm * 10 = 42.4 mm. The uv values: -1.88 to -6.12 span = 4.24, times 10 = 42.4 mm. So uv values are in cm, need to multiply by 10.
SCALE = 10.0

# Outer rectangle in uv (cm) -> yz (mm)
outer_u_min = -6.12 * SCALE  # -61.2 mm
outer_u_max = -1.88 * SCALE  # -18.8 mm
outer_v_min = 10.88 * SCALE  # 108.8 mm
outer_v_max = 15.12 * SCALE  # 151.2 mm

# Inner rectangle in uv (cm) -> yz (mm)
inner_u_min = -6.0 * SCALE   # -60.0 mm
inner_u_max = -2.0 * SCALE   # -20.0 mm
inner_v_min = 11.0 * SCALE   # 110.0 mm
inner_v_max = 15.0 * SCALE   # 150.0 mm

# Build the profile on YZ plane (x=0)
# Outer rectangle centered at midpoint of u and v
outer_center_u = (outer_u_min + outer_u_max) / 2  # -40.0 mm
outer_center_v = (outer_v_min + outer_v_max) / 2  # 130.0 mm
outer_w = outer_u_max - outer_u_min  # 42.4 mm
outer_h = outer_v_max - outer_v_min  # 42.4 mm

inner_center_u = (inner_u_min + inner_u_max) / 2  # -40.0 mm
inner_center_v = (inner_v_min + inner_v_max) / 2  # 130.0 mm
inner_w = inner_u_max - inner_u_min  # 40.0 mm
inner_h = inner_v_max - inner_v_min  # 40.0 mm

# Create workplane on YZ (x=0)
wp = cq.Workplane("YZ")

# Draw outer rectangle
wp = wp.moveTo(outer_center_v, outer_center_u).rect(outer_h, outer_w, centered=True)

# Draw inner rectangle as a hole (cut)
wp = wp.moveTo(inner_center_v, inner_center_u).rect(inner_h, inner_w, centered=True)

# Extrude along negative x (w direction) by 1120.0 mm
# Since we are on YZ plane, extrude in -x direction (which is -w per design plan)
result = wp.extrude(-1120.0)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
