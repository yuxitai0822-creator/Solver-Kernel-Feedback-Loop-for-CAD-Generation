import cadquery as cq

# Design Plan: SoapCutterBedBack1 v1
# Part: flat_plate_or_panel, extruded rectangle
# Dimensions: length_u = 307.848 mm, width_v = 19.05 mm, extrude_distance = 12.7 mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Origin: bbox_min_corner convention, profile in uv-plane

# Build the rectangle profile in the uv-plane (u = x, v = z, w = y)
# The profile curves define a rectangle from (0,0) to (30.7848, 1.905) in uv-space
# Note: The design plan dimensions show length_u = 307.848, width_v = 19.05
# The uv coordinates in the profile are scaled: 30.7848 * 10 = 307.848, 1.905 * 10 = 19.05
# This matches the unit conversion note: cm_to_mm (x10)
# So the profile is defined in cm, and we multiply by 10 to get mm.

# Create the rectangle in the uv-plane (u = x, v = z)
# The rectangle spans from (0, 0) to (307.848, 19.05) in mm
result = (
    cq.Workplane("XY")
    .rect(307.848, 19.05)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\108851_4d515b10_0005\neg_02/generated.step")
