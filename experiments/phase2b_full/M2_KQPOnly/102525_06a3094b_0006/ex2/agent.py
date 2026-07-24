import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is centered on the sketch plane, then extruded in the +w direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: u = X, v = -Z, w = Y
# The rectangle in UV space: u from -0.565 to 0.565, v from -1.05 to 1.05
# But the actual dimensions are length_u=11.3, width_v=21.0.
# The UV coordinates given are half-extents: 0.565 = 11.3/20? Wait: 11.3/2 = 5.65, not 0.565.
# The design plan says unit conversion applied: cm_to_mm (x10).
# So the UV values are in cm? 0.565 cm = 5.65 mm, which matches half of 11.3 mm.
# Similarly, 1.05 cm = 10.5 mm, half of 21.0 mm.
# So we build a rectangle centered at origin in XY plane, then extrude along Y.

# Build the base rectangle on the XY plane (since u_dir=X, v_dir=-Z, but we can just use XY and extrude along Y)
# Actually, to match the frame: u=X, v=-Z, w=Y.
# So the sketch plane is X-Z (with v reversed). We'll create on XZ plane, then extrude along Y.
# But CadQuery's workplane is easier: we can create on XY and then rotate, or just use the XZ plane.
# Let's use the XZ plane (front view) and extrude in the Y direction.

# Rectangle centered at origin, dimensions: 11.3mm along X, 21.0mm along Z (since v=-Z, but magnitude is same)
result = (cq.Workplane("XZ")
          .center(0, 0)
          .rect(11.3, 21.0)
          .extrude(3.0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102525_06a3094b_0006\\ex2/generated.step")
