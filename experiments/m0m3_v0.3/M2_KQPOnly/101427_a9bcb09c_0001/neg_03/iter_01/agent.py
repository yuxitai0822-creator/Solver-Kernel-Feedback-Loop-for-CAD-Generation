import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5 (in UV frame)
# Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
# Extrude in +w direction by 25.0 mm
# UV frame: u = x, v = -z, w = y (per design plan frame axes)
# So we work on XZ plane, extrude in Y direction
# NOTE: The design plan dimensions are in cm (inferred from unit_conversion_applied: cm_to_mm (x10))
# So we must multiply all UV coordinates by 10 to get mm

OUT_STEP_PATH = r"D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_m0m3\\M2_KQPOnly\\101427_a9bcb09c_0001\\neg_03\\iter_01/generated.step"

# Scale factor: cm to mm
scale = 10.0

# Build the outer rectangle on XZ plane
# Outer: u from -2.5 to 195.5, v from -2.5 to 57.5
# In XZ coordinates: x = u * scale, z = -v * scale (since v_dir = [0,0,-1])
# So outer: x from -2.5*10 to 195.5*10, z from -57.5*10 to 2.5*10
outer_xmin = -2.5 * scale
outer_xmax = 195.5 * scale
outer_zmin = -57.5 * scale  # -57.5*10 = -575
outer_zmax = 2.5 * scale    # -(-2.5)*10 = 25

# Inner: u from 0.0 to 193.0, v from 0.0 to 55.0
# In XZ: x from 0.0*10 to 193.0*10, z from -55.0*10 to 0.0*10
inner_xmin = 0.0 * scale
inner_xmax = 193.0 * scale
inner_zmin = -55.0 * scale
inner_zmax = 0.0 * scale

# Create workplane on XZ (Y is normal)
wp = cq.Workplane("XZ")

# Build outer rectangle
outer = wp.moveTo(outer_xmin, outer_zmin).lineTo(outer_xmax, outer_zmin).lineTo(outer_xmax, outer_zmax).lineTo(outer_xmin, outer_zmax).close()

# Build inner rectangle (as a separate wire for cutting)
inner = cq.Workplane("XZ").moveTo(inner_xmin, inner_zmin).lineTo(inner_xmax, inner_zmin).lineTo(inner_xmax, inner_zmax).lineTo(inner_xmin, inner_zmax).close()

# Extrude outer by 25.0 mm in +Y direction (extrude distance is already in mm)
result = outer.extrude(25.0)

# Cut inner hole: extrude inner wire by same amount and subtract
inner_solid = inner.extrude(25.0)
result = result.cut(inner_solid)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)