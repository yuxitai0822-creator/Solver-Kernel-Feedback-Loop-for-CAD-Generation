import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# The part is a disk (extruded circle) with:
# - Circle center in UV: (11.430000364780426, 0.0) but the profile radius is 4.87045
# - The profile radius from dimensions is 4.87045 mm
# - Extrude distance: 6.8707 mm
# - The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
#   This means the sketch plane is XZ (u=x, v=-z) and extrusion is along +w = +y

# Build the part
# Start with a workplane on the XZ plane (since v_dir is [0,0,-1], the plane normal is along y)
# Actually, the frame says: u_dir = x, v_dir = -z, w_dir = y
# So the sketch plane is defined by u and v, which are x and -z, so the plane normal is w = y
# We'll use workplane "XZ" which has normal along Y

result = (
    cq.Workplane("XZ")
    .circle(4.87045)  # radius from dimensions
    .extrude(6.8707)  # extrude along +Y (positive w direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0002\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
