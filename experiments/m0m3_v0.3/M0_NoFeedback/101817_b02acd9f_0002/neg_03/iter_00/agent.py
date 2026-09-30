import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0002\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: corners at (-6.12, 10.88) to (-1.88, 15.12) in UV plane
# Inner rectangle: corners at (-6.0, 11.0) to (-2.0, 15.0) in UV plane
# Extrude direction: -w (which is -x in world coords since w_dir = [1,0,0])
# Extrude distance: 1120.0 mm
# Frame axes: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# So UV plane is YZ plane (u=z, v=y), extrude along X

# Build on YZ workplane (since u=z, v=y)
wp = cq.Workplane("YZ")

# Outer rectangle centered at midpoint of corners
outer_xmin, outer_xmax = -6.12, -1.88
outer_ymin, outer_ymax = 10.88, 15.12
outer_cx = (outer_xmin + outer_xmax) / 2
outer_cy = (outer_ymin + outer_ymax) / 2
outer_w = outer_xmax - outer_xmin
outer_h = outer_ymax - outer_ymin

# Inner rectangle
inner_xmin, inner_xmax = -6.0, -2.0
inner_ymin, inner_ymax = 11.0, 15.0
inner_cx = (inner_xmin + inner_xmax) / 2
inner_cy = (inner_ymin + inner_ymax) / 2
inner_w = inner_xmax - inner_xmin
inner_h = inner_ymax - inner_ymin

# Build outer profile
outer = wp.moveTo(outer_cx, outer_cy).rect(outer_w, outer_h, centered=True)

# Extrude along X (positive direction since w_dir = [1,0,0] and we extrude -w = -x)
# But we want the body to extend 1120mm in the -x direction from the sketch plane
# So we extrude -1120mm
result = outer.extrude(-1120.0)

# Cut inner hole: create inner rectangle and extrude it as a cutting prism
inner = wp.moveTo(inner_cx, inner_cy).rect(inner_w, inner_h, centered=True)
cut_prism = inner.extrude(-1120.0)
result = result.cut(cut_prism)

exporters.export(result, OUT_STEP_PATH)
