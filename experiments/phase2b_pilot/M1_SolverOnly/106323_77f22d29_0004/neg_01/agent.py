import cadquery as cq

# Build an extruded annulus (bearing cross-section)
# Outer radius: 17.5 mm, Inner radius: 12.5 mm
# Extrude symmetrically along Z for a total distance of 10.0 mm

result = (
    cq.Workplane("XY")
    .circle(17.5)
    .circle(12.5)
    .extrude(10.0, combine=True, both=True)
)

# Export the result to STEP format
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\106323_77f22d29_0004\neg_01/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
