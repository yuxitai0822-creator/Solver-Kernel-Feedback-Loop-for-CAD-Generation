import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102760_26430589_0037\neg_02\iter_00\generated.step"

# Design Plan: extruded circle (disk)
# - Circle radius: 0.8 mm (from dimensions.profiles[0].radius.value)
# - Extrude distance: 4.0 mm (from dimensions.extrude_distance.value)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means sketch plane is XZ (u=x, v=z), extrude along w=y
# - The perturbed radius from the JSON is 0.1 (but design plan says 0.8)
#   We follow the design plan dimensions explicitly.

# Build the disk
result = (
    cq.Workplane("XZ")  # sketch plane: XZ (u=x, v=z)
    .circle(0.8)        # radius from design plan
    .extrude(4.0)       # extrude along Y (w direction)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
