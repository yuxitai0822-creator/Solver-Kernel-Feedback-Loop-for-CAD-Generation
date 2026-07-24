import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 279.4 mm, width_v = 50.8 mm, extrude_distance = 19.05 mm
# The frame uses u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle profile in UV space: (0,0) to (27.94, 5.08) but note the design plan says
# length_u = 279.4, width_v = 50.8. The UV coordinates in the profile are scaled by 10?
# Actually the profile curves show start_uv/end_uv values: 0,0 to 27.94,0 etc.
# 27.94 * 10 = 279.4, 5.08 * 10 = 50.8. So the profile is in cm? The compiler notes say
# unit_conversion_applied: cm_to_mm (x10). So the UV values are in cm, we must multiply by 10.
# But the dimensions field already gives mm values: length_u=279.4, width_v=50.8.
# So we build a rectangle of size 279.4 x 50.8 in the XY plane (since u_dir = X, v_dir = -Z?)
# Actually v_dir = (0,0,-1) means v axis is negative Z. w_dir = (0,1,0) means extrusion along Y.
# So the rectangle lies in the XZ plane? Let's interpret: u_dir = X, v_dir = -Z, so the profile
# is in the X-Z plane (with v reversed). Extrude along w_dir = Y.
# We'll create a rectangle on the XZ plane, then extrude along Y.

# Build the base rectangle: center at origin, size 279.4 x 50.8
# Since v_dir is -Z, we need to orient the rectangle accordingly.
# Simpler: use workplane on XZ plane, draw rectangle centered, extrude along Y.

result = (
    cq.Workplane("XZ")
    .rect(279.4, 50.8, centered=True)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0007\\neg_03/generated.step")
