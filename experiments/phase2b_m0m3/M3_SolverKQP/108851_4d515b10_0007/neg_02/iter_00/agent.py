import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108851_4d515b10_0007\neg_02\iter_00\generated.step"

# Design Plan: extruded rectangle
# Dimensions: length_u = 279.4 mm, width_v = 50.8 mm, extrude_distance = 19.05 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# The rectangle in UV space: u from 0 to 27.94, v from 0 to 5.08
# Note: The design plan says length_u = 279.4, width_v = 50.8, but the profile curves show 27.94 x 5.08
# This is because the design plan dimensions are in mm, but the profile curves are in cm (unit conversion cm->mm x10)
# So 27.94 cm = 279.4 mm, 5.08 cm = 50.8 mm
# The extrude distance is 19.05 mm

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the sketch plane normal is w_dir = [0,1,0])
# The rectangle in UV coordinates: u along X, v along Z (negative direction)
# Start at (0, 5.08) in UV -> (0, 0, -5.08) in XYZ? No, let's think carefully.
# Frame: u_dir = X axis, v_dir = -Z axis, w_dir = Y axis
# So UV (u,v) maps to XYZ: (u, 0, -v)
# The rectangle corners in UV: (0,0), (27.94,0), (27.94,5.08), (0,5.08)
# In XYZ: (0,0,0), (27.94,0,0), (27.94,0,-5.08), (0,0,-5.08)
# But the design plan says length_u = 279.4, width_v = 50.8, so we need to scale by 10
# Actually, the profile curves already have the scaled values (27.94 = 279.4/10, 5.08 = 50.8/10)
# Wait, the design plan says "unit_conversion_applied": "cm_to_mm (x10)"
# So the original was in cm, and we need to work in mm. The profile values 27.94 and 5.08 are in cm.
# In mm: 279.4 x 50.8

# Let's just build the rectangle directly with the mm dimensions
length_mm = 279.4
width_mm = 50.8
extrude_mm = 19.05

# Create workplane on XZ (normal is Y axis)
wp = cq.Workplane("XZ")

# Draw rectangle centered at origin, with dimensions length x width
# The rectangle lies in the XZ plane, with X along length, Z along width
result = wp.rect(length_mm, width_mm).extrude(extrude_mm)

# Export
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")