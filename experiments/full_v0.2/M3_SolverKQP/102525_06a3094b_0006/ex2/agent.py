import cadquery as cq

# Design Plan: rectangular prism (SOP-28 body)
# Dimensions: length_u=11.3 mm, width_v=21.0 mm, extrude_distance=3.0 mm
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# Profile rectangle centered at origin in uv-plane, then extruded along +w

# Build the rectangle profile (centered, in uv-plane)
# u corresponds to x, v corresponds to z (since v_dir=(0,0,-1)), w corresponds to y
# But to keep it simple: we work in standard CQ coordinates (x,y,z) and map:
#   u -> x, v -> z, w -> y
# Rectangle half-dimensions: u_half = 11.3/2 = 5.65, v_half = 21.0/2 = 10.5
# The profile vertices in uv: (5.65, -10.5), (5.65, 10.5), (-5.65, 10.5), (-5.65, -10.5)
# In CQ: (x=u, z=v) -> points: (5.65, -10.5), (5.65, 10.5), (-5.65, 10.5), (-5.65, -10.5)

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .polyline([
        (5.65, -10.5),
        (5.65, 10.5),
        (-5.65, 10.5),
        (-5.65, -10.5),
    ])
    .close()
    .extrude(3.0)  # extrude along +Z (which maps to +w direction)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\102525_06a3094b_0006\ex2/generated.step")
