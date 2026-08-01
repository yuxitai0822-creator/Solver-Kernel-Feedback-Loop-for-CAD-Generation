import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108851_4d515b10_0009\neg_03\iter_00\generated.step"

# Design parameters from the design plan
# Rectangle dimensions (in mm, converted from cm)
length_u = 209.55  # along x-axis
width_v = 57.912   # along z-axis (since v_dir = [0,0,-1])
extrude_distance = 19.05  # along y-axis (w_dir = [0,1,0])

# The design plan specifies:
# u_dir = [1,0,0] (x-axis)
# v_dir = [0,0,-1] (negative z-axis)
# w_dir = [0,1,0] (y-axis)
# So the rectangle is in the XZ plane, extruded along Y

# Create the rectangle on the XZ plane (workplane 'XZ')
# The rectangle spans from (0,0) to (length_u, width_v) in UV coordinates
# But UV maps to: u -> x, v -> z (with v_dir = [0,0,-1], so v positive goes negative z)
# To match the design plan's vertex_projection, we place the rectangle
# with its min corner at origin in the XZ plane

# Build the base workplane
wp = cq.Workplane("XZ")

# Create the rectangle centered at (length_u/2, -width_v/2) to match the UV coordinates
# The design plan shows start_uv = [0, 5.7912] and end_uv = [20.955, 0] etc.
# But the dimensions say length_u = 209.55 and width_v = 57.912
# The perturbed value 4.63296 is not used since we follow the design plan dimensions

# Create rectangle on XZ plane, centered at half dimensions
# The rectangle goes from (0,0) to (length_u, -width_v) in XZ coordinates
# because v_dir = [0,0,-1] means positive v maps to negative z
result = (
    wp
    .center(length_u / 2, -width_v / 2)
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
importers = None
exporters.export(result, OUT_STEP_PATH)
