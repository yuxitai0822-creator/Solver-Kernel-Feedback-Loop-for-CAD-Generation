import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0002\neg_02\iter_00/generated.step"

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: corners at (-1.88, 10.88), (-1.88, 15.12), (-6.12, 15.12), (-6.12, 10.88) in UV plane
# Inner rectangle: corners at (-6.0, 11.0), (-2.0, 11.0), (-2.0, 15.0), (-6.0, 15.0) in UV plane
# Frame axes: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
# Extrude distance: 1120.0 mm along -w direction (i.e., negative X)

# Build on YZ plane (since w_dir is X, and we extrude along -X)
# The UV coordinates map to YZ plane: u -> Z, v -> Y
# Outer rectangle in YZ: Z from -6.12 to -1.88, Y from 10.88 to 15.12
# Inner rectangle in YZ: Z from -6.0 to -2.0, Y from 11.0 to 15.0

# Create outer rectangle on YZ plane
result = (
    cq.Workplane("YZ")
    .center(0, 0)
    .moveTo(-1.88, 10.88)  # Z, Y coordinates
    .lineTo(-1.88, 15.12)
    .lineTo(-6.12, 15.12)
    .lineTo(-6.12, 10.88)
    .close()
    .extrude(1120.0)  # extrude along +X (positive w direction)
)

# Cut inner hole: create inner rectangle and extrude through
inner = (
    cq.Workplane("YZ")
    .center(0, 0)
    .moveTo(-2.0, 11.0)  # Z, Y coordinates
    .lineTo(-2.0, 15.0)
    .lineTo(-6.0, 15.0)
    .lineTo(-6.0, 11.0)
    .close()
    .extrude(1120.0)
)

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
