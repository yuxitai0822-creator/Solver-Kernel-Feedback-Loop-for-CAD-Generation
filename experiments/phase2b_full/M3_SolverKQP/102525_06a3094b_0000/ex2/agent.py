import cadquery as cq

# Design Plan: rectangular prism (SOIC-8 body)
# Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Origin at bbox_min_corner, so we place the rectangle in the XY plane with positive extrusion in Y direction.

# Create rectangle profile centered at origin in the XY plane (u = X, v = Z, w = Y)
# The rectangle spans from -length_u/2 to +length_u/2 in X, and -width_v/2 to +width_v/2 in Z.
length_u = 3.9
width_v = 4.9
extrude_dist = 1.55

# Build the base rectangle on the XY plane (normal = (0,0,1)), then extrude in Y direction.
# Since v_dir = (0,0,-1), the width is along Z axis. We'll create the rectangle in XZ plane.
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(length_u, width_v)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0000\\ex2/generated.step")
