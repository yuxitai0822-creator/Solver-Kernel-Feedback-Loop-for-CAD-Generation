import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 500mm x 300mm (u x v)
# Inner rectangle: 400mm x 200mm (u x v) - offset 5mm from outer edges? 
#   Actually from curves: inner starts at (5,5) and ends at (45,25) in UV space where outer is (0,0)-(50,30)
#   So inner is 40mm x 20mm in UV space, but dimensions say inner_length_u=400, inner_width_v=200
#   This is a scaling issue: UV coords are normalized to 0-50 and 0-30, so multiply by 10
# Extrude distance: 500mm in +w direction

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0006\neg_03\iter_00/generated.step"

# Create the outer rectangle profile (500mm x 300mm)
result = (cq.Workplane("XY")
    .rect(500.0, 300.0, centered=False)
    .extrude(500.0)
)

# Create the inner rectangle profile (400mm x 200mm) and cut it out
# Inner rectangle starts at (5,5) in UV space where outer is (0,0)-(50,30)
# Scale factor: outer is 500x300, UV is 50x30, so scale = 10
# Inner UV: (5,5) to (45,25) -> scaled: (50,50) to (450,250)
# So inner rect is 400mm x 200mm, positioned at (50,50) from origin
inner = (cq.Workplane("XY")
    .rect(400.0, 200.0, centered=False)
    .extrude(500.0)
)

# Position the inner rectangle at the correct location
inner = inner.translate((50.0, 50.0, 0.0))

# Cut the inner volume from the outer box to create the hollow frame
result = result.cut(inner)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
