import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101817_b02acd9f_0001\neg_02\iter_01/generated.step"

# Design Plan: horizontal leg 1
# Extruded rectangular frame (hollow box)
# Outer profile: 40x40 mm square (centered at origin)
# Inner profile: 37.6x37.6 mm square (centered at origin)
# Extrude distance: 520 mm in +Z direction
# Note: The perturbation removes the inner void (E4_void_remove), so we produce a solid block.

# Outer square dimensions (from design plan)
outer_length_u = 40.0  # mm
outer_width_v = 40.0   # mm

# Extrude distance
extrude_distance = 520.0  # mm

# Build the solid block (no inner hole due to perturbation)
result = (
    cq.Workplane("XY")
    .rect(outer_length_u, outer_width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")