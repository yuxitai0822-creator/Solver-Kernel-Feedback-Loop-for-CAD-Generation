import cadquery as cq

# Design Plan: rectangular prism (SOIC-8 body)
# Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle profile is centered at origin in uv-plane with half-dimensions:
#   half_u = 3.9/2 = 1.95, half_v = 4.9/2 = 2.45
# But the profile curves show start_uv = (0.195, -0.245) etc. which are in cm (since unit conversion cm->mm x10).
# So the actual mm half-dimensions are: half_u = 0.195*10 = 1.95 mm, half_v = 0.245*10 = 2.45 mm.
# This matches 3.9 mm x 4.9 mm rectangle.

# Build the rectangle in the XY plane (since u_dir = X, v_dir = Z negative, but we'll use standard XY and then rotate)
# Actually, to match the frame: u_dir = X, v_dir = -Z, w_dir = Y.
# So the profile lies in the X-Z plane (with v along -Z). We'll create a rectangle in XY and then rotate.
# Simpler: create a box directly with dimensions 3.9 x 4.9 x 1.55, centered at origin.
# But the extrude direction is +w = +Y, so the box extends from y=-0.775 to y=0.775.

# Use a workplane on the XZ plane (Y=0), draw rectangle centered, extrude symmetrically or one side.
# The design says one_side extrude in +w direction. So the profile is at y=0, extrude up to y=1.55.
# But the rectangle center is at (0,0) in uv, which maps to (0,0,0) in xyz? 
# The profile curves: start_uv = (0.195, -0.245) in cm -> (1.95, -2.45) in mm.
# So the rectangle corners in uv: (1.95, -2.45), (1.95, 2.45), (-1.95, 2.45), (-1.95, -2.45).
# In the frame: u -> X, v -> -Z, so uv (u,v) maps to (u, 0, -v) in XYZ.
# So corners: (1.95, 0, 2.45), (1.95, 0, -2.45), (-1.95, 0, -2.45), (-1.95, 0, 2.45).
# That's a rectangle in the XZ plane at Y=0, centered at origin.
# Extrude in +w = +Y direction by 1.55 mm.

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(3.9, 4.9, forConstruction=False)
    .extrude(1.55)
)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\102525_06a3094b_0000\neg_02/generated.step")
