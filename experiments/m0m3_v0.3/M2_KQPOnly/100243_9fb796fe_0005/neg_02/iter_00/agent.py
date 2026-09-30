import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0005\neg_02\iter_00\generated.step"

# Design Plan: Drone Leg Left - square strut
# Profile: rectangle 19mm x 19mm (in UV plane)
# Extrude: 200mm along W direction
# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# Profile center at UV origin, then extrude along W

# Build the rectangle profile on the XZ plane (since V is [0,0,-1], U is [1,0,0])
# The rectangle dimensions from design plan: length_u=19.0, width_v=19.0
# Profile vertices in UV: 
#   (-58.2782, -12.0401) to (-58.2782, -13.9401) etc.
#   This gives width = 1.9 in UV? Actually let's compute:
#   u range: -58.2782 to -56.3782 = 1.9
#   v range: -13.9401 to -12.0401 = 1.9
# But design plan says length_u=19.0, width_v=19.0
# The UV coordinates seem to be in cm (since compiler notes say cm_to_mm x10)
# So 1.9 cm = 19 mm. That matches!
# The profile center in UV: u_center = (-58.2782 + -56.3782)/2 = -57.3282
#                           v_center = (-12.0401 + -13.9401)/2 = -12.9901

# We'll build the rectangle centered at origin on XZ plane, then translate
# But simpler: just use the UV coordinates directly, scaled to mm
# UV coordinates are in cm, so multiply by 10 to get mm

# Actually, let's just build a 19x19 rectangle centered at origin on XZ plane
# and extrude 200mm along Y (since W=[0,1,0])

result = (
    cq.Workplane("XZ")
    .rect(19.0, 19.0, centered=True)
    .extrude(200.0)
)

# The result should be a 19x19x200 mm rectangular prism
# centered at origin, aligned with axes

exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")