import cadquery as cq

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin in the UV plane.
# U direction = X axis, V direction = -Z axis, W direction = Y axis.
# Extrude in +W (Y) direction by 2.5 mm.

# Create the rectangle profile on the XZ plane (since V = -Z, we use X and Z)
# The rectangle spans from -4.25 to 4.25 in U (X) and -9.0 to 9.0 in V (Z)
# But note: V direction is [0,0,-1], so positive V maps to negative Z.
# The start_uv and end_uv values: first curve from (0.425, -0.9) to (0.425, 0.9)
# These are in UV coordinates. Since V is -Z, we need to map:
#   U -> X, V -> -Z
# So point (u, v) maps to (u, 0, -v) in 3D.
# The rectangle corners:
#   (0.425, -0.9) -> (0.425, 0, 0.9)
#   (0.425, 0.9) -> (0.425, 0, -0.9)
#   (-0.425, 0.9) -> (-0.425, 0, -0.9)
#   (-0.425, -0.9) -> (-0.425, 0, 0.9)
# This gives width = 0.85 in U (X) and 1.8 in V (Z direction).
# But the dimensions say length_u = 8.5 and width_v = 18.0.
# The UV coordinates are scaled by 10? Actually the values 0.425 and 0.9 are half-dimensions.
# 0.425 * 10 = 4.25, 0.9 * 10 = 9.0. So the rectangle is 8.5 x 18.0.
# The UV coordinates are in cm? The compiler notes say cm_to_mm (x10).
# So the UV values are in cm, and we need to multiply by 10 to get mm.
# Let's build the rectangle directly using the dimensions from the plan.

# Build the rectangle on the XZ plane (Y=0), centered at origin.
# Width along X = 8.5 mm, length along Z = 18.0 mm.
# Then extrude along Y by 2.5 mm.

result = (
    cq.Workplane("XZ")
    .rect(8.5, 18.0, centered=True)
    .extrude(2.5)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\102525_06a3094b_0004\\neg_01/generated.step")
