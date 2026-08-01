import cadquery as cq
from cadquery import exporters
import math

# Design parameters from the design plan
# The design plan specifies a disk (extruded circle) with:
# - Circle center at (11.430000364780426, 0.0) in UV space
# - Circle radius: 4.87045 mm
# - Extrude distance: 6.8707 mm (along +w direction)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the sketch is in the XZ plane (u=x, v=-z), extrude along +w = +y

# The previous script had incorrect center (114.3 instead of 11.43) and incorrect extrude depth (10.306 instead of 6.8707)
# Also the previous script had complex loop handling that is unnecessary for a simple circle

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\106817_bb28b7aa_0002\neg_01\iter_00/generated.step"

# Create a workplane on XZ (since u=x, v=-z, the sketch plane is XZ)
# The center in UV is (11.43, 0.0), which maps to (x=11.43, z=0.0) in XZ plane
# Radius = 4.87045 mm
# Extrude along +y (w direction) by 6.8707 mm

result = (
    cq.Workplane("XZ")
    .moveTo(11.430000364780426, 0.0)
    .circle(4.87045)
    .extrude(6.8707)
)

# Export the result
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
