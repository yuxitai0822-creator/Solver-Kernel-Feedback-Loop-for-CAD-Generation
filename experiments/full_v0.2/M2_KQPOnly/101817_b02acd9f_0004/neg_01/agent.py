import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 1200 mm, width_v = 600 mm, extrude_distance = 20 mm
# The profile is defined in a local frame where:
#   u_dir = (1,0,0) -> x-axis
#   v_dir = (0,0,-1) -> negative z-axis
#   w_dir = (0,1,0) -> y-axis (extrude direction)
# The rectangle corners in UV space:
#   (127.82976, -66.34402) to (7.82976, -66.34402)  -> u range: 7.83 to 127.83, v range: -66.34 to -6.34
#   But the explicit dimensions say length_u=1200, width_v=600.
#   The UV coordinates appear to be offset from origin; we will center the rectangle at origin for simplicity.
#   The extrude direction is +w = +y.

# Build the rectangle centered at origin in the XY plane (since u=x, v=-z, w=y)
# Actually: u_dir = x, v_dir = -z, w_dir = y. So the profile lies in the XZ plane (with v along -z).
# We'll create the rectangle on the XZ plane, then extrude along Y.

length_u = 1200.0  # along x
width_v = 600.0    # along z (but v_dir is -z, so width along z is 600)
extrude_dist = 20.0  # along y

# Create rectangle centered at origin in XZ plane
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\101817_b02acd9f_0004\neg_01/generated.step")
