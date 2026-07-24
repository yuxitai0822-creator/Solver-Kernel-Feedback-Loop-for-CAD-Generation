import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle of size 171.45 mm x 38.1 mm (length_u x width_v)
# Extrude by 6.35 mm in the +w direction

# Create the rectangle profile on the XY plane (z=0)
# The design plan uses a local frame where:
#   u_dir = [1,0,0] (X axis)
#   v_dir = [0,0,-1] (Z axis negative, but we'll use positive Z for simplicity)
#   w_dir = [0,1,0] (Y axis)
# The rectangle vertices in UV space:
#   (0, 0) -> (17.145, 0) -> (17.145, 3.81) -> (0, 3.81)
# Note: The UV coordinates are given in cm (17.145 cm = 171.45 mm, 3.81 cm = 38.1 mm)
# The design plan says unit_conversion_applied: cm_to_mm (x10), so we use mm values directly

# Build the rectangle using CadQuery's box method for simplicity
# The plate spans 171.45 mm in X, 38.1 mm in Z (since v_dir is -Z), and 6.35 mm in Y

result = (
    cq.Workplane("XY")
    .box(171.45, 6.35, 38.1, centered=(False, False, False))
    .translate((171.45/2, 6.35/2, 38.1/2))  # Move so that min corner is at origin
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108850_0dcd5ef1_0002\\neg_01/generated.step")
