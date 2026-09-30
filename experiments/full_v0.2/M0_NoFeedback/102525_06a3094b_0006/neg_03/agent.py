import cadquery as cq

# Create a rectangular prism with dimensions: length_u=11.3, width_v=21.0, extrude_distance=3.0
# The profile is centered at origin in the uv-plane, then extruded in the +w direction.
# According to the design plan, the frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0].
# This means: u = X, v = -Z, w = Y.
# The rectangle in uv coordinates: u from -0.565 to 0.565, v from -1.05 to 1.05.
# But the dimensions given are length_u=11.3, width_v=21.0, so the rectangle should be 11.3 x 21.0.
# The profile curves show half-extents: u half = 0.565, v half = 1.05, which matches 11.3/2=5.65? Wait, 0.565*10=5.65, but 11.3/2=5.65. So the uv values are in cm? The compiler notes say cm_to_mm (x10). So the uv values are in cm, and we need to multiply by 10 to get mm.
# Actually, the design plan says unit is mm, but the compiler notes say cm_to_mm (x10). So the uv coordinates are in cm, and we need to scale by 10.
# Let's interpret: half-extents in uv: u=0.565 cm = 5.65 mm, v=1.05 cm = 10.5 mm. So full dimensions: 11.3 mm x 21.0 mm. That matches.
# So we can just use the dimensions directly: length_u=11.3, width_v=21.0.
# The rectangle is centered at origin in uv-plane, so we create a rectangle centered at (0,0) with width=11.3 (along u) and height=21.0 (along v).
# Then extrude along w direction (which is Y axis) by 3.0 mm.

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0006\\neg_03/generated.step")
