import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the UV plane, then extruded in the +W direction.
# Note: The design plan uses a local frame with u_dir=(1,0,0), v_dir=(0,1,0), w_dir=(0,0,1).
# The rectangle corners in UV coordinates: start at (-3.9, 6.8) to (0, 0) but the dimensions are 39.0 x 68.0.
# The UV coordinates given: start_uv = (-3.9, 6.8), end_uv = (0, 6.8), etc.
# This describes a rectangle from u=-3.9 to u=0 (length 3.9) and v=0 to v=6.8 (width 6.8).
# However, the explicit dimensions say length_u=39.0, width_v=68.0. There is a unit conversion note: cm_to_mm (x10).
# So the UV coordinates are in cm? Actually the plan says unit is mm, but the compiler notes say cm_to_mm (x10).
# The UV coordinates (-3.9, 6.8) etc. are likely in cm, so multiply by 10 to get mm: -39, 68, etc.
# Let's interpret: start_uv = (-3.9, 6.8) -> (-39, 68) in mm, end_uv = (0, 6.8) -> (0, 68), etc.
# So the rectangle spans u from -39 to 0 (length 39 mm) and v from 0 to 68 (width 68 mm).
# We'll create a rectangle centered or positioned accordingly. Since the origin convention is bbox_min_corner,
# we can place the rectangle such that its min corner is at (0,0) in the UV plane? But the UV coords suggest
# the rectangle is in the negative u and positive v quadrant. We'll just create a rectangle with the given dimensions
# and then extrude. To match the exact coordinates, we'll use a workplane and then offset.

result = (
    cq.Workplane("XY")
    .center(-19.5, 34.0)  # center of rectangle: u from -39 to 0 -> center at -19.5, v from 0 to 68 -> center at 34
    .rect(39.0, 68.0)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102175_699d5e7c_0003\neg_02/generated.step")