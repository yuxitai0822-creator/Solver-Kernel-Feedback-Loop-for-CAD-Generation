import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle in the UV plane, then extruded in the W direction
# From the design plan:
#   - length_u = 95.25 mm (along X axis)
#   - width_v = 571.5 mm (along Z axis, since v_dir = [0,0,-1])
#   - extrude distance = 19.05 mm (along Y axis, since w_dir = [0,1,0])
# The profile coordinates in UV space:
#   start_uv = (9.525, 57.15)  -> this is the top-right corner
#   end_uv = (9.525, 0.0)      -> bottom-right
#   start_uv = (0.0, 57.15)    -> top-left
#   end_uv = (0.0, 0.0)        -> bottom-left
# So the rectangle spans from u=0 to u=9.525 and v=0 to v=57.15
# But the dimensions say length_u=95.25 and width_v=571.5
# The UV coordinates appear to be scaled by 10 (since compiler notes say cm_to_mm x10)
# Actually 9.525*10 = 95.25 and 57.15*10 = 571.5, so the UV values are in cm
# We'll use the explicit dimensions directly: 95.25 x 571.5 mm

# Build the rectangle centered at origin for simplicity, then extrude
result = (
    cq.Workplane("XY")
    .rect(95.25, 571.5)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\101269_f084ba14_0023\\neg_01/generated.step")
