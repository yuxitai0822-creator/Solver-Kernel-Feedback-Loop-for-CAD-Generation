import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
# The design plan specifies:
# - Circle center in UV: (11.430000364780426, 0.0) but the profile center_uv is (114.300004, 0.0)
#   The compiler note says cm_to_mm (x10) was applied, so the original center was 11.43 cm = 114.3 mm
# - Circle radius: 4.87045 mm (from dimensions.profiles[0].radius)
# - Extrude distance: 6.8707 mm (from dimensions.extrude_distance)
# - The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
#   This means the sketch plane is XZ (u=x, v=-z), and extrusion is along w=y

CENTER_X = 114.300004  # mm
CENTER_Z = 0.0  # mm (center_uv[1] = 0.0)
RADIUS = 4.87045  # mm
EXTRUDE_DISTANCE = 6.8707  # mm

# Build the model
# Workplane on XZ plane (since v_dir = [0,0,-1], the sketch plane normal is y)
# We'll use the XZ workplane which has normal in Y direction
result = (
    cq.Workplane("XZ")
    .moveTo(CENTER_X, CENTER_Z)
    .circle(RADIUS)
    .extrude(EXTRUDE_DISTANCE)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0002\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)