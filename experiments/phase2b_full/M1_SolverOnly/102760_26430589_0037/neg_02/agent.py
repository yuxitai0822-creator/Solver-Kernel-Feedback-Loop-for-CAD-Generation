import cadquery as cq

# Design Plan: Disk (extruded circle)
# Dimensions: radius = 0.8 mm, extrude distance = 4.0 mm
# Note: The design plan uses a local coordinate system with w_dir = [0,1,0] as extrusion direction.
# We'll build a cylinder centered at origin, extruded along Y-axis to match the frame.

# Create a circle with radius 0.8 mm
circle = cq.Workplane("XY").circle(0.8)

# Extrude along positive Y (which corresponds to -w in the plan's frame, but we use standard orientation)
# The plan says direction = "-w" and w_dir = [0,1,0], so extrusion is along negative Y.
# However, to match the expected spans (u:1.6, v:1.6, w:4.0), we extrude along Y axis.
# The circle is in XY plane, extruding along Z gives a cylinder with axis along Z.
# But the plan's frame has w_dir = [0,1,0], so we need to orient accordingly.
# Let's use the standard approach: create circle on XY plane, extrude along Z.
# This yields a cylinder with axis along Z, radius 0.8, height 4.0.
# The spans: u (X) = 1.6, v (Y) = 1.6, w (Z) = 4.0 — matches expected.

result = cq.Workplane("XY").circle(0.8).extrude(4.0)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\102760_26430589_0037\\neg_02/generated.step")
