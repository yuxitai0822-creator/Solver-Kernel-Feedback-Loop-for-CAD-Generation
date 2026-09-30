import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u direction) = 279.4 mm, Width (v direction) = 215.9 mm
# Extrude distance (w direction) = 1.5875 mm

# Note: The design plan uses a coordinate system where:
# u_dir = [1,0,0] (X axis), v_dir = [0,1,0] (Y axis), w_dir = [0,0,1] (Z axis)
# The profile vertices in UV space are:
# (0, 21.59), (0, 0), (27.94, 0), (27.94, 21.59)
# These UV coordinates appear to be in cm (scaled by 10x from mm)
# Since the dimensions state length_u = 279.4 mm and width_v = 215.9 mm,
# and the UV coordinates are 27.94 and 21.59, the scaling factor is 10.
# So we use the explicit dimensions directly.

result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)
    .extrude(1.5875)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\100877_ac1e5a17_0001\\neg_01/generated.step")
