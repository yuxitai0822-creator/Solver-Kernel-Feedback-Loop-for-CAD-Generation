import cadquery as cq

# Design Plan: extruded circle (disk) with radius 7.5 mm and height 20.0 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the circle lies in the u-v plane (x-z plane) and extrudes along w (y-axis)

# Create the circle profile on the xz-plane (u-v plane)
# Center at origin, radius = 7.5 mm
circle = cq.Workplane("XZ").circle(7.5)

# Extrude along the positive y-axis (w direction) by 20.0 mm
result = circle.extrude(20.0)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\104524_f829aab2_0001\neg_03/generated.step")
