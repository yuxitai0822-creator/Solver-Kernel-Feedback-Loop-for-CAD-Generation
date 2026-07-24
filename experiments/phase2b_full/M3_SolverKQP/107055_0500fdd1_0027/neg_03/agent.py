import cadquery as cq

# Design Plan: Washer (2)
# Dimensions: outer_radius=3.49, inner_radius=2.0, thickness=0.36

# Create the washer by extruding an annulus (circle with hole)
# Using the frame: u_dir=[1,0,0], v_dir=[0,-1,0], w_dir=[0,0,-1]
# The profile is in the uv-plane, extrude along +w direction

# Build the outer circle (radius 3.49)
outer = cq.Workplane("XY").circle(3.49)

# Build the inner circle (radius 2.0) as a hole
result = outer.circle(2.0).extrude(0.36)

# The above creates a solid with a through hole (washer)
# Note: The frame indicates v_dir is [0,-1,0] and w_dir is [0,0,-1],
# but since the washer is symmetric, orientation doesn't affect the shape.

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\107055_0500fdd1_0027\\neg_03/generated.step")
