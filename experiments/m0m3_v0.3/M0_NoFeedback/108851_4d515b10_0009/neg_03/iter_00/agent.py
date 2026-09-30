import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterLeg1 v1
# Extruded rectangle: 209.55 mm x 57.912 mm x 19.05 mm
# The profile is a rectangle in the XZ plane, extruded along Y.
# The rectangle corners in UV space: (0,0), (20.955,0), (20.955,5.7912), (0,5.7912)
# But the dimensions say length_u=209.55, width_v=57.912.
# The UV coordinates in the design plan are in cm (since compiler notes say cm_to_mm x10).
# So the actual rectangle in mm is: width=209.55 mm (along U), height=57.912 mm (along V).
# The UV coordinates given: (0,0) to (20.955,0) to (20.955,5.7912) to (0,5.7912) are in cm.
# After cm->mm conversion: 20.955 cm = 209.55 mm, 5.7912 cm = 57.912 mm.
# So we build a rectangle of size 209.55 x 57.912 in the XZ plane, then extrude 19.05 mm along Y.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108851_4d515b10_0009\neg_03\iter_00/generated.step"

# Build the rectangle in the XZ plane (workplane='XZ')
# The rectangle is centered at (104.775, 28.956) in XZ coordinates
# Width along X = 209.55, Height along Z = 57.912
result = (
    cq.Workplane("XZ")
    .center(209.55/2, 57.912/2)
    .rect(209.55, 57.912, centered=True)
    .extrude(19.05)  # extrude along Y (positive direction)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
