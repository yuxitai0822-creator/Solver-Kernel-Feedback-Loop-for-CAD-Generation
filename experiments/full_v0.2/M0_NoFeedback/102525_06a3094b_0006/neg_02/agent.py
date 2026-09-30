import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is a rectangle centered at origin in the u-v plane.
# u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Extrude in +w direction (positive y) by 3.0mm

# Create the rectangle profile on the XZ plane (since v_dir is -Z, w_dir is Y)
# The rectangle spans from -5.65 to 5.65 in u (X) and -1.05 to 1.05 in v (Z)
# But note: v_dir = (0,0,-1), so positive v maps to negative Z.
# The start_uv and end_uv coordinates are given in the profile curves.
# Let's build the rectangle directly using CadQuery's 2D primitives.

# We'll work in the XZ plane (normal = Y axis), then extrude in +Y direction.
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(11.3, 2.1)  # length_u=11.3, width_v=2.1? Wait, width_v is 21.0, but the profile shows v from -1.05 to 1.05 = 2.1mm?
    # Actually the design plan says width_v = 21.0, but the profile curves show v range [-1.05, 1.05] which is 2.1.
    # There's a discrepancy: the profile curves are in uv space, and the dimensions say width_v=21.0.
    # The unit conversion note says cm_to_mm (x10). So the profile uv values are in cm? 
    # The profile curves show v from -1.05 to 1.05 (cm) which becomes -10.5 to 10.5 mm = 21.0 mm. Yes!
    # Similarly u from -0.565 to 0.565 (cm) becomes -5.65 to 5.65 mm = 11.3 mm.
    # So we need to scale the profile by 10x to get mm.
    # Let's use the dimensions directly: length_u=11.3, width_v=21.0
    .rect(11.3, 21.0)
    .extrude(3.0)  # extrude in +Y (w direction) by 3.0mm
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\102525_06a3094b_0006\neg_02/generated.step")