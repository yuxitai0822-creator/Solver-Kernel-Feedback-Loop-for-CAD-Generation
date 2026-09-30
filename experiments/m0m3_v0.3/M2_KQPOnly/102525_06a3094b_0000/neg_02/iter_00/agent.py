import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102525_06a3094b_0000\neg_02\iter_00\generated.step"

# Design Plan: rectangular prism with dimensions 3.9mm x 4.9mm x 1.55mm
# The profile is centered at origin, extruded in +Z direction
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means: u=X, v=-Z, w=Y
# So the rectangle is in XZ plane (u,v) and extrudes along Y (w)

# Rectangle dimensions from design plan:
length_u = 3.9  # along X
width_v = 4.9   # along Z (but v_dir is [0,0,-1], so width is along Z)
extrude_distance = 1.55  # along Y

# Build the part
# Workplane XZ matches the frame: u=X, v=-Z (cq uses positive Z, so we need to handle sign)
# The rectangle is centered at origin in the sketch plane
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Verify dimensions (optional, but good for debugging)
# The resulting solid should have bounding box: X: [-1.95, 1.95], Y: [0, 1.55], Z: [-2.45, 2.45]

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
print(f"Bounding box: {result.val().BoundingBox()}")
