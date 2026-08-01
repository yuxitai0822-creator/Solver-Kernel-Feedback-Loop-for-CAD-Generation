import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Drone Leg - square strut
# Extruded rectangle: 19.0 x 19.0 mm profile, extruded 130.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: center at (-57.2782, -12.9901), size 1.9 x 1.9 mm
# Note: The profile coordinates in the design plan are in UV space.
# The rectangle spans from u=-58.2782 to u=-56.3782 (width=1.9) and v=-13.9401 to v=-12.0401 (height=1.9).
# However, the dimensions table says length_u=19.0, width_v=19.0.
# This is a unit conversion issue: the original was 1.9 cm = 19 mm.
# The profile coordinates are in cm (original units), so we must scale by 10 to get mm.
# After scaling: u_center = (-58.2782 + -56.3782)/2 * 10 = -573.282 mm, v_center = (-13.9401 + -12.0401)/2 * 10 = -129.901 mm
# Width = 1.9 * 10 = 19 mm, Height = 1.9 * 10 = 19 mm

# Build the part
# Workplane: XZ plane (since w_dir = [0,1,0] is normal to XZ)
# The rectangle is in the UV plane, which maps to XZ in world coordinates.
# u_dir = [1,0,0] (X axis), v_dir = [0,0,-1] (negative Z axis)
# So in the XZ plane: u -> X, v -> -Z

# Center of rectangle in UV (original cm): u_c = (-58.2782 + -56.3782)/2 = -57.3282, v_c = (-13.9401 + -12.0401)/2 = -12.9901
# Scale to mm: u_c_mm = -573.282, v_c_mm = -129.901
# In XZ plane: x_center = u_c_mm = -573.282, z_center = -v_c_mm = 129.901 (since v_dir = [0,0,-1])

# Extrude in +w direction = [0,1,0] (Y axis) for 130 mm

result = (
    cq.Workplane("XZ")
    .center(-573.282, 129.901)  # center in XZ plane
    .rect(19.0, 19.0)  # 19 mm x 19 mm rectangle
    .extrude(130.0)  # extrude 130 mm along Y (positive w direction)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\100243_9fb796fe_0006\neg_03\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)