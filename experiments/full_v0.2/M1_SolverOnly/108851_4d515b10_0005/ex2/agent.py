import cadquery as cq

# Create a rectangular plate based on the design plan
# The profile is a rectangle with dimensions:
#   length_u = 307.848 mm (along x-axis)
#   width_v = 19.05 mm (along z-axis, since v_dir = [0,0,-1])
# Extrude distance = 12.7 mm (along y-axis, since w_dir = [0,1,0])

# Create the rectangle profile on the XY plane (z=0)
# The profile coordinates in UV space:
#   start at (0, 1.905) -> (0, 0) -> (30.7848, 0) -> (30.7848, 1.905) -> back to start
# Note: The UV coordinates are scaled: U ranges 0 to 30.7848, V ranges 0 to 1.905
# But the actual dimensions are length_u=307.848 and width_v=19.05
# The UV coordinates appear to be in cm (since compiler notes say cm_to_mm x10)
# So we need to multiply by 10 to get mm: 30.7848*10 = 307.848, 1.905*10 = 19.05

# Build the plate using a rectangle centered at origin for simplicity
# The plate spans: x from -153.924 to 153.924, z from -9.525 to 9.525
# Extrude along y-axis by 12.7 mm

result = (
    cq.Workplane("XY")
    .rect(307.848, 19.05)  # width along x, height along z
    .extrude(12.7)  # extrude along y (positive direction)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\108851_4d515b10_0005\ex2/generated.step")