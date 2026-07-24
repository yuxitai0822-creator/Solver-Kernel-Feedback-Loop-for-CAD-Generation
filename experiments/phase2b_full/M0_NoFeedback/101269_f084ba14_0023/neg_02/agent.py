import cadquery as cq

# Create a rectangular profile based on the design plan
# The profile is defined in the UV plane where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis (so positive V goes in -Z direction)
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# The rectangle corners in UV coordinates:
#   (0,0), (9.525,0), (9.525,57.15), (0,57.15)
# But note: the design plan says length_u = 95.25, width_v = 571.5
# The UV coordinates given are 9.525 and 57.15, which are 1/10 of the actual dimensions.
# This is because the compiler notes say "unit_conversion_applied: cm_to_mm (x10)"
# So the actual dimensions in mm are: length_u = 95.25, width_v = 571.5
#
# The extrude distance is 19.05 mm along +w (Y axis)

# Build the rectangle in the XY plane (since u=X, v=-Z, we need to map carefully)
# Actually, let's build it directly in the XY plane and then extrude along Y

# The profile in UV: u from 0 to 95.25, v from 0 to 571.5
# Mapping: u -> X, v -> -Z (since v_dir = (0,0,-1))
# So the rectangle in XYZ: X from 0 to 95.25, Z from -571.5 to 0

result = (
    cq.Workplane("XY")
    .rect(95.25, 571.5, centered=False)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\101269_f084ba14_0023\neg_02/generated.step")
