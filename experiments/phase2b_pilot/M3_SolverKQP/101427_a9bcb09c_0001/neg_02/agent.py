import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\101427_a9bcb09c_0001\neg_02/generated.step"

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# Dimensions from the design plan (in mm)
outer_length_u = 1980.0
outer_width_v = 600.0
inner_length_u = 1930.0
inner_width_v = 550.0
extrude_distance = 25.0

# Build the rectangular frame by subtracting the inner box from the outer box
outer_box = cq.Workplane("XY").box(outer_length_u, outer_width_v, extrude_distance)
inner_box = cq.Workplane("XY").box(inner_length_u, inner_width_v, extrude_distance)

result = outer_box.cut(inner_box)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
