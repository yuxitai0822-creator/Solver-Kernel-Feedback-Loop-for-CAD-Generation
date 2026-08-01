import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle plate
# Dimensions: length_u=1200.0 mm, width_v=600.0 mm, extrude_distance=20.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle corners in UV space:
#   (127.82976131535646, -66.34402294937294) -> (7.829761315356478, -66.34402294937294)
#   (127.82976131535646, -6.344022949372942) -> (127.82976131535646, -66.34402294937294)
#   (7.829761315356478, -6.344022949372942) -> (127.82976131535646, -6.344022949372942)
#   (7.829761315356478, -66.34402294937294) -> (7.829761315356478, -6.344022949372942)
# The rectangle width in U = 127.82976131535646 - 7.829761315356478 = 120.0
# The rectangle height in V = -6.344022949372942 - (-66.34402294937294) = 60.0
# But design plan says length_u=1200.0, width_v=600.0 -> scaling factor 10x
# The UV coordinates are in cm (original), converted to mm by multiplying by 10
# So: U range = 120.0 * 10 = 1200.0 mm, V range = 60.0 * 10 = 600.0 mm
# Extrude along w_dir (Y axis) by 20.0 mm

# Build the rectangle in the XZ plane (since v_dir is [0,0,-1], w_dir is [0,1,0])
# The sketch plane normal is w_dir = [0,1,0], so we work in XZ plane

# Rectangle center in UV space:
center_u = (127.82976131535646 + 7.829761315356478) / 2.0  # = 67.82976131535647
center_v = (-6.344022949372942 + -66.34402294937294) / 2.0  # = -36.34402294937294

# Dimensions in UV space (original cm units)
width_u = 127.82976131535646 - 7.829761315356478  # = 120.0
height_v = -6.344022949372942 - (-66.34402294937294)  # = 60.0

# Convert to mm (multiply by 10)
width_u_mm = width_u * 10.0  # = 1200.0
height_v_mm = height_v * 10.0  # = 600.0
center_u_mm = center_u * 10.0
center_v_mm = center_v * 10.0

# Build the plate
# Workplane normal is [0,1,0] (Y axis), so we use XZ plane
result = (
    cq.Workplane("XZ")
    .center(center_u_mm, center_v_mm)
    .rect(width_u_mm, height_v_mm, centered=True)
    .extrude(20.0)  # extrude along Y axis (positive direction)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0004\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
