import cadquery as cq

# Outer rectangle: 50mm x 30mm
outer_rect = cq.Workplane("XY").rect(50, 30)

# Inner rectangle: 40mm x 20mm (centered, offset 5mm from outer edges)
inner_rect = cq.Workplane("XY").rect(40, 20)

# Create rectangular frame profile by subtracting inner from outer
frame_profile = outer_rect.cut(inner_rect)

# Extrude the frame profile 500mm in the +Z direction
result = frame_profile.extrude(500)

# Export the result to STEP file
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\104453_aba0f2d1_0006\neg_03/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
