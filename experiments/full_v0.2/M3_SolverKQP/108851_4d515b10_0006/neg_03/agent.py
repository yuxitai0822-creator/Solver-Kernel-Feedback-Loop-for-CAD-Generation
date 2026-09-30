import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 95.25 mm
# Width (v): 19.05 mm
# Height (w): 12.7 mm

# The design plan specifies a rectangle in the uv-plane with:
# u from 0 to 9.524999999999999 (but note: dimensions say length_u = 95.25)
# v from 0 to 1.905 (but dimensions say width_v = 19.05)
# The profile coordinates appear to be in cm (divided by 10), so we multiply by 10 to get mm.
# Actually the compiler notes say "unit_conversion_applied: cm_to_mm (x10)",
# so the profile values are in cm and need to be scaled by 10 to get mm.

# Profile rectangle in uv-plane (u, v coordinates):
# start_uv: (0.0, 1.905) -> (0.0, 19.05) in mm
# end_uv: (0.0, 0.0) -> (0.0, 0.0) in mm
# end_uv: (9.524999999999999, 0.0) -> (95.25, 0.0) in mm
# end_uv: (9.524999999999999, 1.905) -> (95.25, 19.05) in mm
# back to start: (0.0, 1.905) -> (0.0, 19.05) in mm

# The extrude direction is +w, where w is along the y-axis (from frame definition).
# Frame: u_dir = [1,0,0] (x-axis), v_dir = [0,0,-1] (negative z-axis), w_dir = [0,1,0] (y-axis)
# So the rectangle is in the xz-plane (u=x, v=-z), extruded along y (w).

# Build the profile in the xz-plane (y=0):
# Points: (0, 0, -19.05), (0, 0, 0), (95.25, 0, 0), (95.25, 0, -19.05)
# But v_dir is [0,0,-1], so v=0 maps to z=0, v=1.905 maps to z=-1.905*10 = -19.05

# Let's build using a simple box approach for clarity:
# The part is a rectangular prism with dimensions 95.25 x 12.7 x 19.05 (x, y, z)
# where x = u, y = w (extrude direction), z = -v (since v_dir = [0,0,-1])

result = cq.Workplane("XY").box(95.25, 12.7, 19.05).translate((95.25/2, 12.7/2, -19.05/2))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0006\\neg_03/generated.step")
