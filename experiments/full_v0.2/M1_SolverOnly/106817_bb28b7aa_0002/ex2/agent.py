import cadquery as cq

# Design Plan: thumb screw (disk)
# Profile: circle with radius 4.87045 mm, center at (11.430000364780426, 0.0) in UV
# Extrude: distance 6.8707 mm along +w direction
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# The circle center in UV is (11.43, 0). In the local frame, this translates to:
#   center = u_dir * u + v_dir * v = (1,0,0)*11.43 + (0,0,-1)*0 = (11.43, 0, 0)
# The circle lies in the plane defined by u and v axes (i.e., the XY plane in local frame).
# Extrude direction is +w = (0,1,0).

# Build the circle at the correct location
center = cq.Vector(11.430000364780426, 0, 0)
radius = 4.87045

# Create the circle wire in the XY plane (u-v plane) at z=0
circle = cq.Workplane("XY").moveTo(center.x, center.y).circle(radius)

# Extrude along the w direction (positive Y) by 6.8707 mm
result = circle.extrude(6.8707)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106817_bb28b7aa_0002\\ex2/generated.step")
