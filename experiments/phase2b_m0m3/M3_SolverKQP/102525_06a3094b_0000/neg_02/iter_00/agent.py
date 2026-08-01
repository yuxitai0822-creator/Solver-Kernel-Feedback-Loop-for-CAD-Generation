import cadquery as cq
from cadquery import exporters

# Design Plan: SOIC-8 body
# Dimensions: length_u=3.9 mm, width_v=4.9 mm, extrude_distance=1.55 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means: u is X, v is -Z, w is Y
# Profile rectangle in UV plane: center at (0,0), half-widths 1.95 and 2.45
# Extrude along +w (Y direction) by 1.55 mm

# Build the rectangle on the XZ plane (since v_dir is -Z, but we can use XZ directly)
# The rectangle spans from -1.95 to 1.95 in X, and -2.45 to 2.45 in Z
# Then extrude along Y by 1.55

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(3.9, 4.9, centered=True)
    .extrude(1.55)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102525_06a3094b_0000\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)