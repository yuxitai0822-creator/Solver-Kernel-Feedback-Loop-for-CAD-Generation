import cadquery as cq

# Create a rectangular plate based on the design plan
# Profile dimensions: length_u = 95.25 mm, width_v = 571.5 mm
# Extrude distance: 19.05 mm in the +w direction

# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> X, v -> -Z, w -> Y
# So the rectangle is in the X-Z plane (using u and v), extruded along Y (w)

# Create the rectangle profile in the XZ plane
# The profile vertices from the design plan (in uv coordinates):
# (0,0), (9.525,0), (9.525,57.15), (0,57.15)
# But these are in uv space where u ranges 0-9.525 and v ranges 0-57.15
# The actual dimensions are length_u=95.25 and width_v=571.5
# The uv coordinates appear to be scaled by 10 (9.525*10=95.25, 57.15*10=571.5)
# So we use the actual dimensions directly

length_u = 95.25  # along X
width_v = 571.5   # along Z (negative direction per v_dir)
extrude_dist = 19.05  # along Y

# Build the plate: rectangle in XZ plane, extruded in Y direction
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v)
    .extrude(extrude_dist)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\101269_f084ba14_0023\ex2/generated.step")
