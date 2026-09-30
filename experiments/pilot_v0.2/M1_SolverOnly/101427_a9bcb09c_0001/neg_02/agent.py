import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\101427_a9bcb09c_0001\neg_02"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

# Ensure output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Outer rectangle dimensions (from outer ring UV coordinates)
outer_length = 198.0  # 195.5 - (-2.5) = 198.0 mm
outer_width = 60.0    # 57.5 - (-2.5) = 60.0 mm

# Inner rectangle dimensions (from inner ring UV coordinates)
inner_length = 193.0  # 193.0 - 0.0 = 193.0 mm
inner_width = 55.0    # 55.0 - 0.0 = 55.0 mm

# Extrude distance
extrude_dist = 25.0

# Build the rectangular frame by extruding the difference of outer and inner rectangles
result = (cq.Workplane("XY")
            .rect(outer_length, outer_width)
            .rect(inner_length, inner_width)
            .extrude(extrude_dist))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
