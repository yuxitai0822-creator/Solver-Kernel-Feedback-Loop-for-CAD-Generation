import cadquery as cq
from cadquery import exporters
import math

# Design Plan: rectangular prism 3.9 x 4.9 x 1.55 mm (perturbed extrude depth 2.325 mm)
# Build rectangle on XZ plane, extrude along Y (positive direction)

# Rectangle dimensions from design plan
length_u = 3.9  # along X
width_v = 4.9   # along Z (since v_dir = [0,0,-1] in design plan, but we use positive Z for simplicity)
extrude_distance = 2.325  # perturbed value (original 1.55 mm)

# Create workplane on XZ (normal = Y)
wp = cq.Workplane("XZ")

# Build rectangle centered at origin
result = wp.center(0, 0).rect(length_u, width_v).extrude(extrude_distance)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0000\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)
