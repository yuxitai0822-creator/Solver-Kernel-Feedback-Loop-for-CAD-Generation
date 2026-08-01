import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101427_a9bcb09c_0001\neg_03\iter_02/generated.step"

# Design Plan: rectangular frame with outer dimensions ~1980mm x 600mm, inner ~1930mm x 550mm, extruded 25mm
# The kernel feedback consistently shows through_void_count expected 1 but actual 0.
# The issue is that cutThruAll() may not be creating a proper through hole in some CAD kernels.
# We will use a different approach: create the outer box, then subtract the inner box using a boolean cut.

# Outer rectangle dimensions (from design plan curves, scaled by 10 from cm to mm)
outer_xmin = -2.5 * 10  # -25
outer_xmax = 195.5 * 10  # 1955
outer_ymin = -2.5 * 10   # -25
outer_ymax = 57.5 * 10   # 575

# Inner rectangle dimensions (from design plan curves, scaled by 10)
inner_xmin = 0.0 * 10    # 0
inner_xmax = 193.0 * 10  # 1930
inner_ymin = 0.0 * 10    # 0
inner_ymax = 55.0 * 10   # 550

# Extrude distance (25mm)
extrude_dist = 25.0

# Build the outer box
outer_box = (
    cq.Workplane("XZ")
    .center((outer_xmin + outer_xmax) / 2, (outer_ymin + outer_ymax) / 2)
    .rect(outer_xmax - outer_xmin, outer_ymax - outer_ymin)
    .extrude(extrude_dist)
)

# Build the inner box (to be subtracted)
inner_box = (
    cq.Workplane("XZ")
    .center((inner_xmin + inner_xmax) / 2, (inner_ymin + inner_ymax) / 2)
    .rect(inner_xmax - inner_xmin, inner_ymax - inner_ymin)
    .extrude(extrude_dist)
)

# Perform boolean cut to create the through hole
result = outer_box.cut(inner_box)

# Export
exporters.export(result, OUT_STEP_PATH)