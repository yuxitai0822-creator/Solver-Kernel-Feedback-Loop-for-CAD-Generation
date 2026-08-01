import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\106817_bb28b7aa_0004\neg_01\iter_00\generated.step"

# Design parameters from the design plan (converted to mm)
# Outer radius: 5.5372 mm
# Inner radius: 1.9812 mm
# Center in UV plane: (-25.400001, 12.7) - but we'll center at origin for simplicity
# Extrude distance: 1.3208 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the sketch plane is XZ (u=x, v=-z), extrude along Y (w)

outer_radius = 5.5372
inner_radius = 1.9812
thickness = 1.3208

# Build the washer centered at origin on the XZ plane, extruding in Y direction
result = (
    cq.Workplane("XZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(thickness)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")