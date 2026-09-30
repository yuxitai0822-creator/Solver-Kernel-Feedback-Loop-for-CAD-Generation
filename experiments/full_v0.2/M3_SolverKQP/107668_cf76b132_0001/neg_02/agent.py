import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion: 132.5 mm? Wait, the design plan says outer_radius=132.5, inner_radius=75.0, but the profile radius is 13.249999999999998 and 7.499999999999998. The dimensions section says outer_radius=132.5, inner_radius=75.0. The compiler notes say unit_conversion_applied: cm_to_mm (x10). So the profile radii are in cm? Actually the profile radii are 13.25 and 7.5, which when multiplied by 10 give 132.5 and 75.0. So we use the profile radii directly (they are already in mm after conversion? Let's check: the design plan says unit is mm, but compiler notes say cm_to_mm (x10). So the profile radii 13.25 and 7.5 are in cm, and we need to multiply by 10 to get mm. But the dimensions section already gives 132.5 and 75.0 in mm. So we should use the dimensions values: outer_radius=132.5, inner_radius=75.0, extrude_distance=100.0.

# Build the annulus by extruding a circle and subtracting a smaller circle
# Using the frame: u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# This means the extrusion direction is +w = [1,0,0] (along x-axis)
# The profile lies in the uv-plane (y-z plane)

# Create the outer circle on the yz-plane (x=0)
outer = cq.Workplane("YZ").circle(132.5).extrude(100.0)

# Create the inner circle to subtract
inner = cq.Workplane("YZ").circle(75.0).extrude(100.0)

# Subtract inner from outer to get the annulus
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\107668_cf76b132_0001\neg_02/generated.step")
