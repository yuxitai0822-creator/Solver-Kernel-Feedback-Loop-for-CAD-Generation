import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\102525_06a3094b_0004\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan specifies an extruded rectangle forming a rectangular prism.
# Dimensions: length_u = 8.5 mm, width_v = 18.0 mm, extrude_distance = 2.5 mm
# Origin convention: bbox_min_corner
# Frame: u_dir = [1, 0, 0], v_dir = [0, 0, -1], w_dir = [0, 1, 0]
# This means the sketch is on the XZ plane (normal = Y), extruded along +Y.
# The profile spans from u=0 to u=8.5 (X), and v=0 to v=-18.0 (Z).
# Since v_dir is -Z, v=0 maps to Z=0, and v=-18.0 maps to Z=18.0.
# This correctly places the bounding box minimum at the origin (0, 0, 0).

result = (
    cq.Workplane("XZ")
    .transformed(offset=(0, 0, 0))
    .rect(8.5, 18.0)
    .extrude(2.5)
)

cq.exporters.export(result, OUT_STEP_PATH)
