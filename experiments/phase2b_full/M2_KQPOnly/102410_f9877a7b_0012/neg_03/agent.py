import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Dimensions: outer radius = 6.0 mm, inner radius = 4.25 mm, extrude distance = 12.0 mm
# The annulus is centered at (0,0) in the sketch plane, extruded along +w direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the sketch plane is the u-v plane (x-z plane in world), extrusion along w (y-axis).
# To match the frame, we create the annulus on the xz-plane and extrude along y.

# Create the outer circle (radius 6.0)
outer = cq.Workplane("XZ").circle(6.0)

# Create the inner circle (radius 4.25) as a hole
inner = cq.Workplane("XZ").circle(4.25)

# Combine: outer circle with inner hole, then extrude along y-axis (positive direction) by 12.0 mm
result = outer.cut(inner).extrude(12.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102410_f9877a7b_0012\\neg_03/generated.step")
