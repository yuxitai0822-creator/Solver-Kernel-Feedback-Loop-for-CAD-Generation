import cadquery as cq

# Design Plan: extruded circle (disk) with radius 0.8 mm and height 4.0 mm
# The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the extrusion direction is -w = (0,-1,0) (negative Y in world)
# But for simplicity, we create the disk in the XY plane and then rotate/translate
# to match the frame. However, the simplest approach: create a cylinder along Y axis
# with radius 0.8 and height 4.0, centered at origin, then rotate to align with frame.
# Actually, the frame has w_dir = (0,1,0), so the extrusion is along -w = (0,-1,0).
# The profile is a circle of radius 0.08? Wait: profile radius is 0.08, but dimensions
# say radius 0.8. The profile curves have radius 0.08000000000000002, but dimensions
# say radius 0.8. This is likely a scaling issue (cm to mm conversion factor 10).
# The explicit dimension says radius 0.8 mm, so we use 0.8 mm.
# The extrude distance is 4.0 mm.

# Build the disk: a cylinder with radius 0.8 mm, height 4.0 mm, centered at origin.
# The cylinder axis will be along Y (since w_dir = (0,1,0) and extrusion is -w).
# But to match the frame: u_dir = X, v_dir = -Z, w_dir = Y.
# So the profile circle is in the X-Z plane (u-v plane), extruded along Y (w direction).
# Since extrusion is -w, we extrude in negative Y direction.

# Create the cylinder centered at origin, axis along Y, radius 0.8, height 4.0
result = cq.Workplane("XZ").circle(0.8).extrude(4.0, both=False)  # extrudes in +Y by default
# But we need extrusion in -Y direction. So we can extrude both=False and then translate.
# Actually, Workplane("XZ") creates a plane with normal Y, and extrude goes in +Y.
# To get -Y, we can extrude 4.0 and then move the result down by 2.0 to center it.
# Or we can use a negative distance: extrude(-4.0) which goes in -Y.
# Let's use extrude(-4.0) to get the extrusion in -w direction.

result = cq.Workplane("XZ").circle(0.8).extrude(-4.0)

# Now the result is a cylinder from y=0 to y=-4.0, centered at y=-2.0.
# The design plan expects the part to be centered at origin? The frame origin is at
# bbox_min_corner, but we don't have explicit position. The validation expects
# spans: u=1.6 (diameter), v=1.6 (diameter), w=4.0 (height). So the part should be
# centered at origin for the spans to be symmetric. Let's center it.

# Rebuild centered: extrude both ways or translate.
result = cq.Workplane("XZ").circle(0.8).extrude(2.0, both=True)  # extrudes 2.0 in +Y and -Y, total 4.0

# This gives a cylinder from y=-2.0 to y=2.0, centered at origin.
# The spans: u (X) = 1.6, v (Z) = 1.6, w (Y) = 4.0. Correct.

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102760_26430589_0037\neg_01/generated.step")