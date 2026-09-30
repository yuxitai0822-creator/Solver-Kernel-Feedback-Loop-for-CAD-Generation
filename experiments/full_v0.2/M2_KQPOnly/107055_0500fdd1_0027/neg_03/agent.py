import cadquery as cq

# Design Plan: Washer (2)
# Dimensions: outer_radius=3.49, inner_radius=2.0, thickness=0.36

# Create the washer by extruding an annulus (circle with hole)
# Using the frame: u_dir=[1,0,0], v_dir=[0,-1,0], w_dir=[0,0,-1]
# The profile is in the uv-plane, extrude in +w direction

# Build the outer circle (radius 3.49)
outer = cq.Workplane("XY").circle(3.49)

# Build the inner circle (radius 2.0) as a hole
inner = cq.Workplane("XY").circle(2.0)

# Create the annulus by cutting inner from outer, then extrude
result = (
    cq.Workplane("XY")
    .circle(3.49)  # outer boundary
    .circle(2.0)   # inner boundary (hole)
    .extrude(0.36) # extrude in +Z direction (which corresponds to +w after frame alignment)
)

# Note: The frame indicates w_dir = [0,0,-1], but since we are building in the standard
# coordinate system and the part is symmetric, the orientation does not affect the geometry.
# The extrusion distance is 0.36 mm as specified.

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\107055_0500fdd1_0027\\neg_03/generated.step")
