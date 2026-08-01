import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterBackBar1 v1
# Extruded rectangle: 279.4 mm x 50.8 mm x 19.05 mm
# Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# Profile in uv-plane: rectangle from (0,5.08) to (27.94,0) in uv coordinates
# Note: uv coordinates are scaled by 10 (cm->mm conversion)
#   u: 0 to 27.94 -> 0 to 279.4 mm
#   v: 0 to 5.08 -> 0 to 50.8 mm
# Extrude along +w direction by 19.05 mm

# Build the rectangle in the uv-plane (XZ plane in CadQuery, since v is along -Z)
# Workplane: XZ (u along X, v along -Z)
# Rectangle corners in uv: (0,5.08) -> (0,0) -> (27.94,0) -> (27.94,5.08) -> back to (0,5.08)
# In XZ coordinates: u->X, v-> -Z (since v_dir = [0,0,-1])
# So: (X, Z) = (u, -v)
# Points:
#   (0, -5.08) -> (0, 0) -> (27.94, 0) -> (27.94, -5.08) -> back to (0, -5.08)
# Scale by 10: multiply all coordinates by 10

scale = 10.0  # cm to mm conversion

# Rectangle dimensions in mm after scaling
length_u_mm = 27.94 * scale  # 279.4 mm
width_v_mm = 5.08 * scale    # 50.8 mm
extrude_mm = 19.05

# Build the rectangle in XZ plane
# Center the rectangle at origin for simplicity, then translate if needed
# Rectangle in uv: from (0,5.08) to (27.94,0) -> width in u = 27.94, height in v = 5.08
# In XZ: width along X = 27.94*scale, height along Z = 5.08*scale
# But the rectangle starts at (0,5.08) in uv, which is (0, -5.08*scale) in XZ
# and ends at (27.94*scale, 0) in XZ
# So the rectangle is offset from origin.

# Let's build it explicitly using polyline
wp = cq.Workplane("XZ")

# Start at (0, -5.08*scale) = (0, -50.8)
# Then line to (0, 0)
# Then line to (27.94*scale, 0) = (279.4, 0)
# Then line to (279.4, -50.8)
# Then close back to (0, -50.8)

pts = [
    (0.0, -width_v_mm),  # (0, -50.8)
    (0.0, 0.0),          # (0, 0)
    (length_u_mm, 0.0),  # (279.4, 0)
    (length_u_mm, -width_v_mm)  # (279.4, -50.8)
]

# Build wire from points
wire = cq.Workplane("XZ").polyline(pts).close().wire()

# Extrude along +w direction = +Y (since w_dir = [0,1,0])
result = wire.extrude(extrude_mm)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108851_4d515b10_0007\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
