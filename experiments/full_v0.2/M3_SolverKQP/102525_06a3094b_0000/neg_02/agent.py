import cadquery as cq

# Create a rectangular prism with dimensions:
# length_u = 3.9 mm (along x-axis)
# width_v = 4.9 mm (along z-axis, since v_dir = [0,0,-1])
# extrude_distance = 1.55 mm (along y-axis, since w_dir = [0,1,0])
#
# The profile is centered at the origin in the uv-plane.
# The rectangle corners in uv: u from -0.195 to 0.195, v from -0.245 to 0.245
# (these are half-dimensions: 3.9/2 = 1.95? Wait, the plan says 0.195 and 0.245,
#  but the dimensions are 3.9 and 4.9. The uv coordinates in the plan are in cm?
#  Actually the plan says unit_conversion_applied: cm_to_mm (x10).
#  So the uv values 0.195 and 0.245 are in cm, which become 1.95 mm and 2.45 mm.
#  Half of 3.9 mm = 1.95 mm, half of 4.9 mm = 2.45 mm. That matches.
#  So we use the uv values directly as mm after conversion? No, the plan says
#  the unit is mm, but the uv values are 0.195 and 0.245. With cm_to_mm x10,
#  these become 1.95 and 2.45. So we multiply by 10.

# Build the rectangle in the XY plane (u=x, v=z, w=y)
# The frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So we work in the XZ plane for the profile, extrude along Y.

# Half dimensions in mm (after cm->mm conversion)
hu = 0.195 * 10  # = 1.95 mm
hv = 0.245 * 10  # = 2.45 mm

# Create the rectangle centered at origin in XZ plane
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(2*hu, 2*hv)
    .extrude(1.55)  # extrude along Y (positive direction)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\102525_06a3094b_0000\neg_02/generated.step")
