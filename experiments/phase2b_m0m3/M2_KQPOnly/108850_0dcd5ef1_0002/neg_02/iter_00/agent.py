import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u = 171.45 mm, width_v = 38.1 mm, extrude_distance = 6.35 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# Profile rectangle in UV plane: u from 0 to 17.145, v from 0 to 3.81
# Note: The design plan values are in cm originally (17.145 cm = 171.45 mm, 3.81 cm = 38.1 mm, 0.635 cm = 6.35 mm)
# The perturbation changes the u-span from 171.45 to 205.74 mm (20.574 cm)

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1] and w_dir is [0,1,0])
# The rectangle in UV coordinates: u along X, v along Z (negative direction)
# So we create a rectangle in XZ plane with width along X = 205.74 mm, height along Z = 38.1 mm
# Then extrude along Y (w_dir = [0,1,0]) by 6.35 mm

result = (
    cq.Workplane("XZ")
    .rect(205.74, 38.1, centered=False)
    .extrude(6.35)
)

exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108850_0dcd5ef1_0002\neg_02\iter_00/generated.step")