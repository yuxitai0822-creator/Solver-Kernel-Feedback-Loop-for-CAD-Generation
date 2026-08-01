import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0004\neg_02\iter_00\generated.step"

# Design parameters from the design plan (converted to mm)
# Outer radius: 5.5372 mm (from dimensions.outer_radius)
# Inner radius: 1.9812 mm (from dimensions.inner_radius)
# Center: (-25.400001, 12.7) in UV plane
# Extrude distance: 1.3208 mm along +w direction
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the sketch plane is XZ (u=x, v=-z), extrude along +w = +y

outer_radius = 5.5372
inner_radius = 1.9812
center_x = -25.400001
center_z = -12.7  # because v_dir = [0,0,-1], so v coordinate maps to -z
height = 1.3208

# Build the washer
# Workplane on XZ (since u=x, v=-z, the sketch plane is XZ)
result = (
    cq.Workplane("XZ")
    .moveTo(center_x, center_z)
    .circle(outer_radius)
    .extrude(height)
    .faces("<Y")  # select bottom face (extrude goes +Y)
    .workplane()
    .hole(inner_radius * 2, height)  # through hole
)

exporters.export(result, OUT_STEP_PATH)
