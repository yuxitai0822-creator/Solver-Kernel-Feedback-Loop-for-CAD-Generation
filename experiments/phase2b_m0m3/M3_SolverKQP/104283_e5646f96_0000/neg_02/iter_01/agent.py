import cadquery as cq
from cadquery import exporters

# Design Plan parameters
# Profile: circle at center_uv = (-15.0, 10.0) with radius 12.5 mm
# Extrude: 75.0 mm along +w direction (which is +X in world frame)
# The frame has u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# So the sketch plane is YZ (u-v plane), extrude along X (w direction)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104283_e5646f96_0000\neg_02\iter_01/generated.step"

# Build the part
# Workplane on YZ (since u_dir = (0,0,-1) and v_dir = (0,1,0), the plane normal is w_dir = (1,0,0))
# In cadquery, we can use Workplane("YZ") which has normal along X
result = (
    cq.Workplane("YZ")
    .moveTo(-15.0, 10.0)  # center_uv in the sketch plane
    .circle(12.5)  # radius from dimensions
    .extrude(75.0)  # extrude along +X (w direction)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)