import cadquery as cq

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin in the u-v plane.
# u direction = x-axis, v direction = z-axis (negative), w direction = y-axis
# Extrude in +w direction (y-axis) by 2.5 mm

# Create the rectangle profile centered at origin
# Width along u (x) = 8.5 mm, length along v (z) = 18.0 mm
# The rectangle vertices from the plan are at u = ±0.425, v = ±0.9 (scaled by 10?)
# Actually the plan says length_u = 8.5, width_v = 18.0, so half extents are 4.25 and 9.0
# The uv coordinates in the plan: start_uv = [0.425, -0.9] etc. These appear to be half-extents in cm? 
# But the explicit dimensions say 8.5 and 18.0 mm. The uv coordinates are likely in cm (since unit conversion cm_to_mm x10).
# So the rectangle in mm: half-width along u = 4.25 mm, half-width along v = 9.0 mm.

# Build the rectangle in the xz-plane (u=x, v=z), then extrude along y (w direction)
result = (cq.Workplane("XZ")
          .center(0, 0)
          .rect(8.5, 18.0)
          .extrude(2.5))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0004\\neg_03/generated.step")
