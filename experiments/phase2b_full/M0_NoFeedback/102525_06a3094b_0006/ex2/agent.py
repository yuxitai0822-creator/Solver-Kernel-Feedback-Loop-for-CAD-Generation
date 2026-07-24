import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is centered on the sketch plane, extruded in the +w direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: u = X, v = -Z, w = Y
# The rectangle in UV coordinates: u from -0.565 to 0.565, v from -1.05 to 1.05
# But the actual dimensions are length_u = 11.3, width_v = 21.0.
# The UV coordinates given are half-extents: 0.565 = 11.3/20? Wait, 11.3/2 = 5.65, not 0.565.
# The design plan says unit conversion applied: cm_to_mm (x10). So the UV values are in cm?
# Actually, the profile curves show start_uv and end_uv values like 0.5649999999999998, -1.05.
# These are half-extents in cm: 0.565 cm = 5.65 mm, 1.05 cm = 10.5 mm.
# So the rectangle half-width along u = 5.65 mm, half-height along v = 10.5 mm.
# Total length_u = 2 * 5.65 = 11.3 mm, width_v = 2 * 10.5 = 21.0 mm. Correct.
# Extrude distance = 3.0 mm along +w (which is +Y).

# Build the rectangle centered at origin in the XZ plane (since v_dir = -Z, u_dir = X)
# Actually, sketch plane: u = X, v = -Z, so the plane normal is w = Y.
# We'll create a rectangle centered at (0,0) in the XZ plane, then extrude along Y.

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0006\\ex2/generated.step")
