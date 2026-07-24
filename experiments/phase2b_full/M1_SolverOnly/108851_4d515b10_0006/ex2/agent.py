import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm
# Width (v): 19.05 mm
# Height (w): 12.7 mm

# The profile is a rectangle in the uv-plane, extruded along the w-direction.
# According to the design plan:
#   u_dir = [1, 0, 0]  (X axis)
#   v_dir = [0, 0, -1] (negative Z axis)
#   w_dir = [0, 1, 0]  (Y axis)
# So the rectangle lies in the XZ plane (with v along -Z), extruded along Y.

# Build the rectangle profile on the XZ plane (workplane with normal Y)
result = (
    cq.Workplane("YZ")  # Start on YZ plane, but we'll work in XZ
    .center(0, 0)
    .rect(95.25, 19.05)  # width along X, height along Z (since v_dir = -Z, we use positive Z)
    .extrude(12.7)  # extrude along Y (positive direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0006\\ex2/generated.step")
