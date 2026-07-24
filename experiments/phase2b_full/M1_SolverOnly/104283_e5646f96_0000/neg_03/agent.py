import cadquery as cq

# Create a cylinder (extruded circle) based on the design plan.
# The design plan specifies:
# - Profile: circle with radius 12.5 mm (converted from cm: 1.25 cm = 12.5 mm)
# - Center in UV: (-15.0, 10.0) mm (converted from cm: -1.5, 1.0 cm)
# - Extrude distance: 75.0 mm along +w direction (which is the x-axis in the local frame)
# - The local frame has u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
#   So w is along x-axis, u is along -z, v is along y.
# - The origin convention is bbox_min_corner, but we place the circle center at (-15, 10) in the UV plane.
#   In the local frame, a point (u,v) maps to: origin + u*u_dir + v*v_dir.
#   Since we don't have an explicit origin, we assume the sketch plane is at w=0 (x=0) and the circle center
#   is at (-15, 10) in the UV coordinates, which translates to world coordinates:
#   x = 0 (w=0), y = v = 10, z = -u = 15 (since u_dir = (0,0,-1)).
#   So the circle center is at (0, 10, 15) in world coordinates.
# - The extrude direction is +w, which is along the x-axis (1,0,0).
# - The result should be a cylinder of radius 12.5 mm, length 75 mm, centered at (0,10,15) and oriented along x.

# Build the cylinder using a workplane on the YZ plane (since we want to extrude along x).
# We'll create a circle on the YZ plane at (y=10, z=15) and extrude along x from 0 to 75.

result = (
    cq.Workplane("YZ")
    .center(10, 15)  # move to (y=10, z=15) in the YZ plane
    .circle(12.5)    # radius 12.5 mm
    .extrude(75.0)   # extrude along x (positive direction) by 75 mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104283_e5646f96_0000\\neg_03/generated.step")
