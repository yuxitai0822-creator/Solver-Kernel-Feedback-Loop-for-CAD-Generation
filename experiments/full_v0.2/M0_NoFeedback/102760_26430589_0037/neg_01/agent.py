import cadquery as cq

# Design Plan: disk with radius 0.8 mm and height 4.0 mm
# The coordinate system uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the extrusion is along -w, i.e., along negative y-axis.
# However, for a simple disk, we can create a cylinder along the y-axis.

# Create a cylinder with radius 0.8 mm and height 4.0 mm
# The cylinder is centered at origin, axis along y-direction
result = cq.Workplane("XY").circle(0.8).extrude(4.0)

# The above creates a cylinder along Z. To match the frame orientation:
# u_dir = X, v_dir = -Z, w_dir = Y, so we need to rotate the cylinder
# to align its axis with Y (w_dir).
# Actually, the extrusion direction is -w = -Y, so the cylinder axis should be Y.
# Let's create it properly:
result = cq.Workplane("XZ").circle(0.8).extrude(4.0)  # extrudes along Y

# Now the cylinder is centered at origin, radius 0.8, height 4.0 along Y
# The span along u (X) = 1.6, v (Z) = 1.6, w (Y) = 4.0, matching validation intents

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102760_26430589_0037\neg_01/generated.step")
