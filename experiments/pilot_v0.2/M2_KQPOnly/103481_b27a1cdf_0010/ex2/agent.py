import cadquery as cq

# Build a rectangular prism: 101.6 x 101.6 x 38.1 mm
# The profile rectangle is centered at the origin in the XY plane,
# spanning from (-5.08, -5.08) to (5.08, 5.08) in the local sketch coordinates (inches converted to cm then mm).
# In mm, the rectangle spans from (-50.8, -50.8) to (50.8, 50.8), yielding length_u = 101.6 and width_v = 101.6.

result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)
    .extrude(38.1)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\103481_b27a1cdf_0010\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
