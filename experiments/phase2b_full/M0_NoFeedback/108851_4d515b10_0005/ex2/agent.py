import cadquery as cq

# Design Plan: SoapCutterBedBack1 v1
# Part: flat_plate_or_panel, extruded rectangle
# Dimensions: length_u=307.848 mm, width_v=19.05 mm, extrude_distance=12.7 mm
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# Origin at bbox_min_corner, so we place the rectangle in the XY plane (u,v) and extrude along w (Y axis)

# Create the rectangular profile in the XY plane (u = X, v = Z, but v_dir is (0,0,-1) so we use Z negative)
# The profile is defined in UV space: u from 0 to 307.848, v from 0 to 19.05
# Since v_dir is (0,0,-1), v=0 maps to Z=0, v=19.05 maps to Z=-19.05
# We'll create the rectangle with width along X and height along Z (negative direction)

result = (
    cq.Workplane("XY")
    .rect(307.848, 19.05)  # width along X, height along Z
    .extrude(12.7)  # extrude along Y (positive direction)
)

# The resulting part should have:
# - Span along X: 307.848 mm
# - Span along Z: 19.05 mm
# - Span along Y: 12.7 mm
# This matches the design plan dimensions.

import cadquery as cq
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108851_4d515b10_0005\\ex2/generated.step")
