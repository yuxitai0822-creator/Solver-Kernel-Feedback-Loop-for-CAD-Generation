import cadquery as cq

# Create a rectangular plate based on the design plan
# The profile is a rectangle with dimensions:
#   length_u = 307.848 mm (along x-axis)
#   width_v = 19.05 mm (along z-axis, since v_dir = [0,0,-1])
# Extrude distance = 12.7 mm along w_dir = [0,1,0] (y-axis)

# Create the rectangle in the XY plane (we'll position it appropriately)
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> x, v -> -z, w -> y
# So the rectangle lies in the XZ plane and extrudes along Y

# We'll build a box directly since it's a simple extruded rectangle
# Dimensions: 307.848 (x) x 12.7 (y) x 19.05 (z)
# But note: the profile is in uv space where u is length (307.848) and v is width (19.05)
# The extrude is along w (12.7)
# In our coordinate system: u=x, v=-z, w=y
# So the rectangle is in the xz plane, extruded along y

# Create the base rectangle on the XZ plane
result = (
    cq.Workplane("XZ")
    .rect(307.848, 19.05)
    .extrude(12.7)
)

# The resulting box is centered at origin. 
# The design plan uses bbox_min_corner origin convention, but since no specific
# position constraints are given, centered is acceptable.

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108851_4d515b10_0005\ex2/generated.step")
