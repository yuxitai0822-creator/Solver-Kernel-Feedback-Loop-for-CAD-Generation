import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame
# Outer rectangle: from (-2.5, 57.5) to (195.5, -2.5) in UV plane
#   U spans 198.0, V spans 60.0 (after unit conversion: cm->mm, original 1980x600 -> 198x60)
# Inner rectangle: from (0, 55) to (193, 0) in UV plane
#   U spans 193.0, V spans 55.0
# Extrude distance: 25.0 mm (original 2.5 cm -> 25 mm)
# Frame axes: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# So sketch is in XZ plane (u=X, v=-Z), extrude along Y (w)

# Build outer rectangle centered at (96.5, 27.5) with size (198, 60)
# Build inner rectangle centered at (96.5, 27.5) with size (193, 55)
# Then extrude 25 mm in +Y direction

result = (
    cq.Workplane("XZ")
    .center(96.5, 27.5)
    .rect(198.0, 60.0)
    .extrude(25.0)
    .faces("<Y")  # select bottom face to cut from
    .workplane()
    .center(96.5, 27.5)
    .rect(193.0, 55.0)
    .cutThruAll()
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101427_a9bcb09c_0001\neg_01\iter_01/generated.step"
exporters.export(result, OUT_STEP_PATH)