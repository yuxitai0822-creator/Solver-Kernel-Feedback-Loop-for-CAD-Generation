import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 171.45 mm, width_v = 38.1 mm, extrude_distance = 6.35 mm
# The profile is a rectangle in the UV plane, then extruded along +W.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: U = X, V = -Z, W = Y
# So the rectangle lies in the XZ plane (with V reversed), extruded along Y.

# Build the rectangle in the XY plane (standard), then rotate/translate to match frame.
# Simpler: create a box directly with the correct dimensions and position.
# The rectangle corners in UV: (0,0) to (17.145, 3.81) but note the design plan says length_u=171.45, width_v=38.1.
# The curves show start_uv (0, 3.81) to (0,0) etc. That's a rectangle of size 17.145 x 3.81 in UV.
# But the dimensions say length_u=171.45, width_v=38.1. There's a factor of 10 (cm to mm conversion).
# The curves are in cm? Actually the compiler note says cm_to_mm (x10). So the UV values are in cm.
# So actual mm: length_u = 171.45 mm, width_v = 38.1 mm.
# The rectangle in UV: from (0,0) to (17.145, 3.81) in cm = (171.45, 38.1) in mm.
# So we just use the mm dimensions directly.

# Frame: u_dir = X, v_dir = -Z, w_dir = Y
# So the rectangle lies in the X-Z plane (with V along -Z).
# We'll create the rectangle in the XZ plane, then extrude along Y.

# Create the rectangle in the XZ plane (Y=0 plane)
# Points: (0,0,0), (171.45,0,0), (171.45,0,-38.1), (0,0,-38.1)
# But v_dir is -Z, so width_v = 38.1 along -Z means from 0 to -38.1.

result = (
    cq.Workplane("XZ")
    .rect(171.45, 38.1, centered=False)
    .extrude(6.35)
)

# The rect is created with lower-left corner at (0,0) in the plane.
# In XZ plane, that means (0,0,0) is one corner, and the rectangle extends to (171.45, 0, -38.1).
# Extrude along Y (positive) gives thickness 6.35.

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\108850_0dcd5ef1_0002\ex2/generated.step")
