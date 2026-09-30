import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk)
# - Circle center in UV: (5.080000162124634, 6.350000202655792) but note the profile center_uv is (50.800002, 63.500002) after cm->mm conversion
# - Radius: 4.7117 mm (from profile radius value)
# - Extrude distance: 12.192 mm (from explicit dimension, not the perturbed 18.288)
# - Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0) -> sketch on XZ plane, extrude along Y
# - The circle center in the sketch plane (XZ) should be (5.080000162124634, 6.350000202655792) in original units,
#   but after cm->mm conversion the profile center_uv is (50.800002, 63.500002). We use the profile center_uv directly.

# Build the disk
result = (
    cq.Workplane("XZ")  # v_dir = (0,0,-1) means v is -Z, u is X, so sketch plane is XZ
    .moveTo(50.800002, 63.500002)  # center in sketch coordinates (u, v) = (X, Z)
    .circle(4.7117)  # radius in mm
    .extrude(12.192)  # extrude along w_dir = (0,1,0) = Y axis
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0003\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)