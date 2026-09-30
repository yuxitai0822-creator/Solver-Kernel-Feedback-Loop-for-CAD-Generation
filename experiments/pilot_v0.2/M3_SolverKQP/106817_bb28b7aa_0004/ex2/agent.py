import cadquery as cq
import os

# Washer dimensions (converted from cm to mm as noted in compiler_notes)
outer_radius = 5.5372
inner_radius = 1.9812
extrude_distance = 1.3208

# Center position in the XY plane (from dimensions center_uv)
center_x = -25.400001
center_y = 12.7

# Build the washer as an extruded annulus
# Create outer circle and extrude, then cut inner circle through
result = (
    cq.Workplane("XY")
    .center(center_x, center_y)
    .circle(outer_radius)
    .extrude(extrude_distance)
    .faces(">Z")
    .workplane()
    .circle(inner_radius)
    .cutThruAll()
)

# Ensure output directory exists
out_dir = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\106817_bb28b7aa_0004\ex2"
os.makedirs(out_dir, exist_ok=True)

# Export to STEP
cq.exporters.export(result, os.path.join(out_dir, "generated.step"))
