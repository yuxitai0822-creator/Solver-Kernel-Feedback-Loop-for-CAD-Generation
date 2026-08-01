import cadquery as cq
from cadquery import exporters

# Design Plan: extruded circle (disk)
# - Circle center in UV: (5.080000162124634, 6.350000202655792) but note unit conversion cm->mm
#   Original center in cm: (5.080000162124634, 6.350000202655792) -> in mm: (50.80000162124634, 63.50000202655792)
# - Radius: 0.4711700000000002 cm -> 4.7117 mm (original), but perturbation changed to 0.5889625000000003 cm -> 5.889625 mm
# - Extrude distance: 12.192 mm
# - Workplane: XZ (since normal is [0,1,0], sketch plane is XZ)

# Parameters (all in mm)
CENTER_X = 50.80000162124634
CENTER_Y = 63.50000202655792
RADIUS = 5.889625  # perturbed radius: 0.5889625 cm = 5.889625 mm
EXT_DIST = 12.192

# Build the disk
result = (
    cq.Workplane("XZ")
    .moveTo(CENTER_X, CENTER_Y)
    .circle(RADIUS)
    .extrude(EXT_DIST)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0003\neg_02\iter_01/generated.step"
exporters.export(result, OUT_STEP_PATH)