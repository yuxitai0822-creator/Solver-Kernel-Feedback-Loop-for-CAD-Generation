import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\106817_bb28b7aa_0002\neg_03\iter_00/generated.step"

# Design Plan parameters:
# - Circle center at (11.430000364780426, 0.0) in UV frame
# - Circle radius = 4.87045 mm (from dimensions.profiles[0].radius)
# - Extrude distance = 6.8707 mm along +w direction
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# - The profile center_uv is given as [11.430000364780426, 0.0] but the radius is 4.87045
# - The outer ring has radius 0.48704499999999984 which seems like a mistake (too small)
# - Using the explicit dimension radius = 4.87045 mm

# Build the part: a simple disk (extruded circle)
# Workplane is XZ (since v_dir = [0,0,-1] means v is along -Z, w is along Y)
# We'll create the circle on the XZ plane and extrude along Y

result = (
    cq.Workplane("XZ")
    .circle(4.87045)  # radius from explicit dimension
    .extrude(6.8707)   # extrude distance along Y (which is +w direction)
)

exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")