import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u-direction) = 171.45 mm, Width (v-direction) = 38.1 mm, Extrude distance (w-direction) = 6.35 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u = X, v = -Z, w = Y
# So the rectangle is in the X-Z plane (width along Z is negative, but we use absolute dimensions)
# We'll create the rectangle on the XY plane and then rotate if needed, but simpler: use workplane on XY
# Since v_dir is [0,0,-1], the rectangle's v dimension is along -Z. We'll just use positive dimensions.

# Create the base rectangle on the XY plane (X = u, Y = w, Z = v)
# Actually, let's follow the frame: u along X, v along -Z, w along Y
# So the profile is in the X-Z plane, with v dimension along Z (but negative direction)
# We'll create a workplane on the XY plane, draw rectangle, then extrude along Y

result = (
    cq.Workplane("XY")
    .rect(171.45, 38.1)  # width along X, height along Z (but we use positive)
    .extrude(6.35)  # extrude along Y (positive w direction)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108850_0dcd5ef1_0002\\neg_01/generated.step")
