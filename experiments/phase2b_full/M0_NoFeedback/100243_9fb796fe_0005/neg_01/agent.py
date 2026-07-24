import cadquery as cq

# Create a rectangular profile in the UV plane
# The profile is a 19mm x 19mm square centered at the origin
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# The profile coordinates in UV space are:
#   u range: [-58.2782, -56.3782]  (width = 1.9, but dimensions say 19.0)
#   v range: [-13.9401, -12.0401]  (height = 1.9, but dimensions say 19.0)
# Wait - the UV coordinates span 1.9 units, but the dimensions say 19.0.
# The compiler note says cm_to_mm (x10) was applied, so the UV coords are in cm?
# Actually the dimensions say 19.0 mm, and the UV coords span 1.9 units.
# This suggests the UV coords are in cm and need to be scaled by 10 to get mm.
# Let's scale the profile by 10 to match the 19mm dimension.

# Create the rectangle in UV space (scaled by 10 to convert cm to mm)
# Original UV corners: (-58.2782, -12.0401) to (-56.3782, -13.9401)
# After scaling by 10: (-582.782, -120.401) to (-563.782, -139.401)
# Width = 19.0, Height = 19.0

# Actually, let's re-examine: the profile is a 19x19 mm square.
# The UV coordinates given span 1.9 units, which after cm->mm conversion becomes 19mm.
# So we should scale the UV coordinates by 10.

# But wait - the extrude distance is 200.0 mm (already in mm).
# The profile dimensions are 19.0 mm x 19.0 mm.
# The UV coordinates in the plan are in cm (since compiler applied cm_to_mm x10).
# So we need to multiply UV coords by 10 to get mm.

scale = 10.0

# Original UV coordinates (in cm)
u1_cm = -58.27820137826746
v1_cm = -12.04014576968157
u2_cm = -56.37820137826746
v2_cm = -13.940145769681571

# Convert to mm
u1 = u1_cm * scale
v1 = v1_cm * scale
u2 = u2_cm * scale
v2 = v2_cm * scale

# Create the rectangle in UV space
# The frame maps: u -> X, v -> -Z, w -> Y
# So the rectangle lies in the X-Z plane (with v inverted)

# Create a workplane on the XZ plane (Y=0)
# In CadQuery, the default workplane is XY, so we need to rotate
# We want: u=X, v=-Z, w=Y
# So the profile is in the XZ plane, and extrude is along Y

# Create the rectangle using the computed coordinates
result = (
    cq.Workplane("XZ")
    .center((u1 + u2) / 2, (v1 + v2) / 2)  # center of rectangle
    .rect(abs(u2 - u1), abs(v2 - v1))  # width and height
    .extrude(200.0)  # extrude along Y (positive w direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\100243_9fb796fe_0005\\neg_01/generated.step")
