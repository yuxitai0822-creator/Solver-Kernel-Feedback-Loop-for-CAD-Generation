import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded circle (disk) with radius 4.7117 mm, extrude distance 12.192 mm
# Center in UV plane: (5.080000162124634, 6.350000202655792) - but we use local coordinates
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So the sketch plane is XZ (u=x, v=-z), extrude along +w = +y

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106817_bb28b7aa_0003\neg_03\iter_00/generated.step"

# Parameters from design plan
radius = 4.7117  # mm
extrude_distance = 12.192  # mm
center_u = 5.080000162124634  # in UV plane
center_v = 6.350000202655792  # in UV plane

# Build the disk
# Using XZ workplane (u=x, v=-z), extrude along Y (+w direction)
result = (
    cq.Workplane("XZ")
    .moveTo(center_u, -center_v)  # v_dir = [0,0,-1], so v coordinate maps to -z
    .circle(radius)
    .extrude(extrude_distance)  # extrude along +Y (which is +w direction)
)

# Export
exporters.export(result, OUT_STEP_PATH)
