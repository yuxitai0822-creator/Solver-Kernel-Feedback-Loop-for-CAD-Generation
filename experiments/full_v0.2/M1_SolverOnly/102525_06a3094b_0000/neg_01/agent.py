import cadquery as cq

# Design Plan: rectangular prism (SOIC-8 body)
# Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle is centered at origin in uv plane, with half-dimensions:
#   half_u = 3.9/2 = 1.95, half_v = 4.9/2 = 2.45
# But the profile curves show start_uv and end_uv values of ±0.195 and ±0.245,
# which are 1/10 of the actual dimensions (due to cm->mm conversion factor 10).
# We use the explicit dimensions: 3.9 x 4.9 mm rectangle, extruded 1.55 mm in +w direction.

# Build the rectangle in the uv-plane (u = x, v = z, w = y)
# The rectangle is centered at (0,0) in uv, with u extent = 3.9, v extent = 4.9
result = (
    cq.Workplane("XY")
    .rect(3.9, 4.9, centered=True)
    .extrude(1.55)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102525_06a3094b_0000\neg_01/generated.step")
