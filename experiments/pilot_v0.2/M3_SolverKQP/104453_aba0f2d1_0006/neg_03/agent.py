import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\104453_aba0f2d1_0006\neg_03/generated.step"

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# Outer rectangle dimensions: 50mm x 30mm
outer_length = 50.0
outer_width = 30.0

# Inner rectangle dimensions: 40mm x 20mm
inner_length = 40.0
inner_width = 20.0

# Extrusion distance: 500mm
extrude_distance = 500.0

# Create the rectangular frame by extruding the difference between outer and inner rectangles
result = (cq.Workplane("XY")
            .rect(outer_length, outer_width)
            .rect(inner_length, inner_width)
            .extrude(extrude_distance))

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
