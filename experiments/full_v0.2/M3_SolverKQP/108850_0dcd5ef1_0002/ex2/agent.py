import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u direction) = 171.45 mm, Width (v direction) = 38.1 mm, Extrude distance (w direction) = 6.35 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle is in the X-Z plane (using u and v), extruded along Y (w direction)

# Create the rectangle profile in the XZ plane
# The rectangle corners in UV coordinates: (0,0), (17.145,0), (17.145,3.81), (0,3.81)
# But note: the design plan dimensions show length_u = 171.45 and width_v = 38.1
# The UV coordinates in the profile are scaled: 17.145 = 171.45/10, 3.81 = 38.1/10
# This is because the source was in cm and converted to mm (x10 factor in compiler_notes)
# So we use the actual dimensions: 171.45 mm x 38.1 mm

# Build the plate
result = (
    cq.Workplane("XZ")
    .rect(171.45, 38.1)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108850_0dcd5ef1_0002\ex2/generated.step")
