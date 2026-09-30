import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is a rectangle centered at origin in the XY plane, extruded in +Z direction.
# From the design plan:
#   - u_dir = [1,0,0] (X axis)
#   - v_dir = [0,0,-1] (Z axis, but negative; we'll use positive Z for extrusion)
#   - w_dir = [0,1,0] (Y axis)
# The rectangle spans from -0.565 to 0.565 in u (X) and -1.05 to 1.05 in v (Z).
# But note: v_dir is [0,0,-1], so the v coordinate maps to -Z.
# The extrude distance is 3.0 mm along +w direction (Y axis).
#
# To match the frame: u=X, v=-Z, w=Y.
# So the rectangle in (u,v) space: u from -0.565 to 0.565, v from -1.05 to 1.05.
# In XYZ: X = u, Z = -v, Y = 0 initially, then extrude along Y.
#
# Let's build the rectangle in the XY plane (Z=0) and extrude along Z to get a simple box.
# But the design plan specifies w_dir = Y, so extrusion is along Y.
# We'll create the rectangle in the XZ plane (Y=0) and extrude along Y.

# Rectangle dimensions:
length_u = 11.3  # along X
width_v = 21.0   # along Z (but v_dir is -Z, so magnitude is 21.0)
extrude_dist = 3.0  # along Y

# Create rectangle centered at origin in XZ plane (Y=0)
# Points: half-lengths
hu = length_u / 2.0  # 5.65
hv = width_v / 2.0   # 10.5

# Build wire from points in XZ plane (Y=0)
pts = [
    (-hu, 0, -hv),
    ( hu, 0, -hv),
    ( hu, 0,  hv),
    (-hu, 0,  hv),
    (-hu, 0, -hv),
]
wire = cq.Workplane("XZ").polyline(pts).close().wire()

# Make face and extrude along Y positive direction
result = cq.Workplane("XZ").polyline(pts).close().extrude(extrude_dist)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102525_06a3094b_0006\neg_01/generated.step")
