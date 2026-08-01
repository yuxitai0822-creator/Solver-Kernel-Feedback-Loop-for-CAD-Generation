import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Workplane: XZ (since v_dir is -Z, normal is Y)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102410_f9877a7b_0012\neg_01\iter_00/generated.step"

# Build the annulus profile on XZ plane (Y is normal)
# Outer circle radius 6.0, inner circle radius 4.25, both centered at origin
result = (
    cq.Workplane("XZ")
    .circle(6.0)          # outer circle
    .circle(4.25)         # inner circle (creates a hole)
    .extrude(12.0)        # extrude along Y (positive direction)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
