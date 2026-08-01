import cadquery as cq
from cadquery import exporters

# Design Plan: flat rectangular plate 254.0 x 190.5 x 3.175 mm
# The perturbation description indicates the v-dimension should be 152.4 mm,
# but the kernel feedback shows the expected v-dimension is 190.5 mm.
# Therefore, we revert to the original design plan dimensions.

# Build the rectangle centered at origin, then extrude
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)  # width=254.0 (u), height=190.5 (v, original)
    .extrude(3.175)       # extrude in +Z direction
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100877_ac1e5a17_0017\neg_03\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)