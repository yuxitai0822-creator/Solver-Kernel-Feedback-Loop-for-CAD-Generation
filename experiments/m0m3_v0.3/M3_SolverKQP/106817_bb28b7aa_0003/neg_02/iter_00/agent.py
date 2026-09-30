import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk)
# - Circle center in UV: (5.080000162124634, 6.350000202655792) but note the profile center_uv is (50.800002, 63.500002) after cm->mm conversion
# - Radius: 4.7117 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance: 12.192 mm along +w direction
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means sketch plane is XZ (u=x, v=z), extrude along +w = +y

# Build the disk
result = (
    cq.Workplane("XZ")
    .circle(4.7117)  # radius in mm
    .extrude(12.192)  # extrude along Y (positive w direction)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0003\neg_02\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)