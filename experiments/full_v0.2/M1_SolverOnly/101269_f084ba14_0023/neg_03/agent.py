import cadquery as cq

# Create a rectangular profile based on the design plan
# The profile is defined in UV space where:
# U direction = [1,0,0] (X axis)
# V direction = [0,0,-1] (negative Z axis)
# W direction = [0,1,0] (Y axis)

# Profile dimensions from the design plan:
# Length along U = 95.25 mm (from 0 to 95.25, but curves show 9.525? Let's check)
# Actually looking at the curves more carefully:
# start_uv: [9.525, 57.15] to [9.525, 0.0]  -> vertical line at u=9.525
# start_uv: [0.0, 57.15] to [9.525, 57.15]  -> horizontal line at v=57.15
# start_uv: [0.0, 0.0] to [0.0, 57.15]      -> vertical line at u=0.0
# start_uv: [9.525, 0.0] to [0.0, 0.0]      -> horizontal line at v=0.0
# So the rectangle spans u: 0 to 9.525, v: 0 to 57.15
# But the dimensions say length_u = 95.25, width_v = 571.5
# This is a 10x scaling factor. The curves are in cm, dimensions in mm.
# The compiler note says "cm_to_mm (x10)" was applied.
# So the actual dimensions in mm are: u: 95.25, v: 571.5

# Let's use the explicit dimensions from the design plan:
length_u = 95.25  # mm
width_v = 571.5   # mm
extrude_distance = 19.05  # mm

# Create the rectangle in the XY plane (since we'll extrude in Z)
# The frame says: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means: U=X, V=-Z, W=Y
# So the profile is in the X-Z plane, and extrude is along Y

# Create workplane on XZ plane (Y=0)
result = (cq.Workplane("XZ")
          .rect(length_u, width_v)
          .extrude(extrude_distance))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101269_f084ba14_0023\\neg_03/generated.step")
