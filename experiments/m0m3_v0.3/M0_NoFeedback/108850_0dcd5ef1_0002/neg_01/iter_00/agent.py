import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle 171.45 x 38.1 x 6.35 mm
# Perturbation: extrude depth = 9.525 mm (0.9525 cm converted to mm)

# Build the rectangle profile on the XZ plane (as per original script)
# The profile coordinates from the design plan:
# start_uv: (0.0, 3.81) -> (0.0, 0.0) -> (17.145, 0.0) -> (17.145, 3.81) -> back to start
# But the dimensions say length_u=171.45, width_v=38.1, so the UV coordinates are scaled by 10
# Actually the design plan says unit conversion cm_to_mm (x10), so the values are in cm originally
# The profile curves show: 0.0, 3.81, 17.145 which are cm values -> mm: 0, 38.1, 171.45

# Create the rectangle centered at origin for simplicity
# Rectangle dimensions: 171.45 mm (u/length) x 38.1 mm (v/width)
# Extrude in +w direction (which is +Y in world coordinates based on frame)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So sketch on XZ plane, extrude in +Y direction

result = (
    cq.Workplane("XZ")
    .rect(171.45, 38.1, centered=True)
    .extrude(9.525)  # perturbed depth: 0.9525 cm = 9.525 mm
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108850_0dcd5ef1_0002\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)