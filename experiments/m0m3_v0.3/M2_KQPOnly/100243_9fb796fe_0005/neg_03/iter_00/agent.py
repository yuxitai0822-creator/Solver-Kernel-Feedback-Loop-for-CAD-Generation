import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0005\neg_03\iter_00/generated.step"

# Design Plan: Drone Leg Left - square strut
# Profile: rectangle 19.0mm x 19.0mm (in UV plane)
# Extrude: 200.0mm along W direction
# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# Profile center in UV: (-57.27820137826746, -12.99014576968157)
# Rectangle corners in UV: 
#   (-58.27820137826746, -12.04014576968157) -> (-58.27820137826746, -13.940145769681571)
#   -> (-56.37820137826746, -13.940145769681571) -> (-56.37820137826746, -12.04014576968157)
# Width in U: 1.9mm, Height in V: 1.9mm (but design says 19.0mm - scaling applied)
# The original data had cm->mm conversion (x10), so 1.9cm = 19.0mm
# The perturbation changed 1.9 to 1.52 (cm) = 15.2mm
# Using perturbed dimensions: width=15.2mm, height=15.2mm, extrude=200.0mm

# Build on XY plane, then transform to match frame
# Frame: U=X, V=-Z, W=Y
# So sketch on XZ plane, extrude along Y

# Rectangle center in UV: (-57.27820137826746, -12.99014576968157)
# Width in U: 1.52 (perturbed from 1.9) -> 15.2mm after cm->mm
# Height in V: 1.52 (perturbed from 1.9) -> 15.2mm after cm->mm

# Using XZ plane for sketch (U=X, V=-Z)
# Center in XZ: x=-57.27820137826746, z=12.99014576968157 (negate V since V=-Z)

result = (
    cq.Workplane("XZ")
    .center(-57.27820137826746, 12.99014576968157)
    .rect(15.2, 15.2)
    .extrude(200.0)
)

exporters.export(result, OUT_STEP_PATH)
