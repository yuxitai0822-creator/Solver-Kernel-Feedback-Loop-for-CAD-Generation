import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: from (-2.5, 57.5) to (195.5, -2.5) in UV plane
#   => width = 198.0, height = 60.0 (in UV coordinates)
# Inner rectangle: from (0.0, 55.0) to (193.0, 0.0)
#   => width = 193.0, height = 55.0
# Extrude direction: +w (which is +Y in world), distance = 25.0 mm
# The UV plane corresponds to XZ in cadquery (since v_dir = [0,0,-1])
# We'll build on workplane 'XZ' and extrude in +Y direction.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0001\neg_02\iter_01\generated.step"

# Build outer rectangle on XZ plane
# UV coordinates: u = X, v = -Z (since v_dir = [0,0,-1])
# Outer: u from -2.5 to 195.5, v from -2.5 to 57.5
# In XZ: x from -2.5 to 195.5, z from -57.5 to 2.5 (negate v)
outer_xmin, outer_xmax = -2.5, 195.5
outer_zmin, outer_zmax = -57.5, 2.5  # v=-2.5 => z=2.5, v=57.5 => z=-57.5

# Inner: u from 0.0 to 193.0, v from 0.0 to 55.0
inner_xmin, inner_xmax = 0.0, 193.0
inner_zmin, inner_zmax = -55.0, 0.0  # v=0 => z=0, v=55 => z=-55

# Create workplane on XZ
wp = cq.Workplane("XZ")

# Build outer rectangle (centered at midpoint for convenience)
outer_cx = (outer_xmin + outer_xmax) / 2
outer_cz = (outer_zmin + outer_zmax) / 2
outer_w = outer_xmax - outer_xmin
outer_h = outer_zmax - outer_zmin

# Build inner rectangle
inner_cx = (inner_xmin + inner_xmax) / 2
inner_cz = (inner_zmin + inner_zmax) / 2
inner_w = inner_xmax - inner_xmin
inner_h = inner_zmax - inner_zmin

# Create the frame by extruding outer rectangle, then cutting inner rectangle
# Step 1: create outer rectangle and extrude in +Y direction by 25.0 mm
result = wp.moveTo(outer_cx, outer_cz).rect(outer_w, outer_h).extrude(25.0)

# Step 2: create inner rectangle as a cutting tool (same extrusion)
cut_wp = cq.Workplane("XZ").moveTo(inner_cx, inner_cz).rect(inner_w, inner_h).extrude(25.0)

# Step 3: subtract inner from outer to create hollow frame
result = result.cut(cut_wp)

# Export
cq.exporters.export(result, OUT_STEP_PATH)