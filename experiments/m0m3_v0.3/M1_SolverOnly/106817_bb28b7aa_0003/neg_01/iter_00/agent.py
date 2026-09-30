import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Extruded circle (disk) with:
# - Circle center in UV: (5.080000162124634, 6.350000202655792) but note unit conversion cm->mm
# - Circle radius: 0.4711700000000002 cm = 4.7117 mm
# - Extrude distance: 12.192 mm (from design plan, not the perturbed value)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means sketch plane is XZ (u=x, v=z), extrude along +w = +y

# Parameters (all in mm)
CENTER_X = 5.080000162124634 * 10  # cm to mm
CENTER_Y = 6.350000202655792 * 10  # cm to mm
RADIUS = 0.4711700000000002 * 10   # cm to mm = 4.7117 mm
EXTRUDE_DIST = 12.192  # mm (from design plan, not perturbed)

# Build the disk
# Workplane on XZ (since v_dir = [0,0,-1] means z is the sketch vertical)
# Actually: u_dir=[1,0,0] (x), v_dir=[0,0,-1] (negative z), w_dir=[0,1,0] (y)
# So sketch plane is XZ, extrude along +Y
result = (
    cq.Workplane("XZ")
    .moveTo(CENTER_X, CENTER_Y)
    .circle(RADIUS)
    .extrude(EXTRUDE_DIST)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0003\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)