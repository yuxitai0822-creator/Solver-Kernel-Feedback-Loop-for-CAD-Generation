import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm, Width (v): 19.05 mm, Height (w): 12.7 mm
# The profile is a rectangle in the uv-plane, extruded along the w-direction.
# Based on the design plan, the frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# This means: u = X, v = -Z, w = Y.
# So the rectangle lies in the XZ-plane (with v reversed) and extrudes along Y.

# Build the rectangle profile on the XY plane (since v_dir is -Z, we can just use standard orientation)
# Actually, to match the frame exactly: u along X, v along -Z, w along Y.
# We'll create a rectangle on the XZ plane (normal Y) with width along X and height along Z.
# But v_dir is -Z, so the rectangle's second dimension should be along -Z.
# The rectangle vertices in uv: (0,0), (9.525,0), (9.525,1.905), (0,1.905)
# These uv values are scaled by 10 (since dimensions are 95.25 and 19.05, and uv max is 9.525 and 1.905).
# So the rectangle in uv space is 9.525 x 1.905, which maps to 95.25 x 19.05 in mm.

# Create the rectangle on the XZ plane (normal Y), centered at origin for simplicity.
# Width along X = 95.25, height along Z = 19.05.
# Then extrude along Y by 12.7 mm.

result = (
    cq.Workplane("XZ")
    .rect(95.25, 19.05, centered=True)
    .extrude(12.7)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108851_4d515b10_0006\neg_02/generated.step")
