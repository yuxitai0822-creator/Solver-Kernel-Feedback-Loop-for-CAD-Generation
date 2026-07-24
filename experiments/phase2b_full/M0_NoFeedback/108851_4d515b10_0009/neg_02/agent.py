import cadquery as cq

# Create a rectangular plate based on the design plan
# The profile is a rectangle with dimensions:
#   length_u = 209.55 mm (along x-axis)
#   width_v = 57.912 mm (along z-axis, since v_dir = [0,0,-1])
# Extrude distance = 19.05 mm along w_dir = [0,1,0] (y-axis)

# Create the rectangle in the XY plane (we'll work in the local frame)
# The profile coordinates from the plan:
#   start_uv = (0.0, 5.7912) -> (0, 5.7912)
#   end_uv = (0.0, 0.0) -> (0, 0)
#   end_uv = (20.955, 0.0) -> (20.955, 0)
#   end_uv = (20.955, 5.7912) -> (20.955, 5.7912)
# Note: The plan dimensions are length_u=209.55, width_v=57.912
# The profile coordinates appear to be in cm (divided by 10) because
# the compiler notes say "cm_to_mm (x10)". So we multiply by 10.
# Actually, the plan says unit is mm, but the profile values are small.
# Let's use the explicit dimensions from the plan: 209.55 x 57.912 mm

# The frame: u_dir = [1,0,0] (x), v_dir = [0,0,-1] (negative z), w_dir = [0,1,0] (y)
# So the rectangle lies in the XZ plane (u along x, v along z)
# Extrude along y (w direction)

# Build the rectangle in the XZ plane
result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\108851_4d515b10_0009\\neg_02/generated.step")
