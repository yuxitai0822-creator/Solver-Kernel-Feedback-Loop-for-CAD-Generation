import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# Profile rectangle corners in UV space:
#   (121.17356129030935, 31.299551148092803) to (-0.7464387096940412, 290.379551148076)
# These are in the UV coordinate system. We need to map to XYZ.
# Since u_dir = X, v_dir = -Z, w_dir = Y, the UV coordinates map to:
#   X = u, Z = -v, Y = 0 (base plane)
# So the rectangle in XYZ is:
#   X: -0.7464 to 121.1736
#   Z: -290.3796 to -31.2996
#   Y: 0 (then extrude in +Y direction by 44.45 mm)

# However, the dimensions in the design plan are much larger: 1219.2 x 2590.8 mm.
# The UV coordinates given are small (range ~122 x 259). This suggests the UV coordinates
# might be in cm (since compiler notes say cm_to_mm x10). Let's check:
#   UV span in u: 121.1736 - (-0.7464) = 121.92 cm = 1219.2 mm ✓
#   UV span in v: 290.3796 - 31.2996 = 259.08 cm = 2590.8 mm ✓
# So the UV coordinates are in cm, and we need to multiply by 10 to get mm.
# But wait - the design plan says unit is mm. The compiler notes say cm_to_mm (x10).
# So the UV coordinates are in cm, and we should convert to mm by multiplying by 10.

# Let's build the rectangle in mm:
# Convert UV (cm) to XYZ (mm):
#   X = u * 10
#   Z = -v * 10
#   Y = 0

# Rectangle corners in UV (cm):
#   (121.17356129030935, 31.299551148092803)  -> top-left in UV
#   (-0.7464387096940412, 31.299551148092803) -> bottom-left in UV
#   (121.17356129030935, 290.379551148076)    -> top-right in UV
#   (-0.7464387096940412, 290.379551148076)   -> bottom-right in UV

# In XYZ (mm):
#   X: -7.464387 to 1211.735613
#   Z: -2903.795511 to -312.995511
#   Y: 0

# Width in X: 1211.735613 - (-7.464387) = 1219.2 mm ✓
# Width in Z: 2903.795511 - 312.995511 = 2590.8 mm ✓

# Extrude in +Y direction by 44.45 mm

# Build the rectangle on the XZ plane (since Y is the extrusion direction)
# Workplane XZ means: X is horizontal, Z is vertical, Y is normal

x_min = -7.4643870969404125
y_min = -2903.79551148076  # This is Z in cadquery (since we're on XZ plane)
x_max = 1211.7356129030936
y_max = -312.99551148092803  # This is Z in cadquery

# Center and size
cx = (x_min + x_max) / 2
cz = (y_min + y_max) / 2
width = x_max - x_min  # 1219.2 mm
height = y_max - y_min  # 2590.8 mm

# Build the model
result = (
    cq.Workplane("XZ")
    .moveTo(cx, cz)
    .rect(width, height, centered=True)
    .extrude(44.45)  # extrude in +Y direction
)

# Export
out_path = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108244_329b1876_0000\neg_01\iter_00\generated.step"
exporters.export(result, out_path)
