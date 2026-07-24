import cadquery as cq

# Create the outer circle (radius 13.25 mm after cm->mm conversion: 132.5 mm? Wait, the design plan says outer_radius value 132.5, but the profile radius is 13.249999999999998. The dimensions section says outer_radius value 132.5, inner_radius value 75.0. The profile radius is 13.25 and 7.5. There is a note: unit_conversion_applied: cm_to_mm (x10). So the profile radii are in cm? Actually the profile radius is 13.25, but dimensions say 132.5. Let's check: The profile radius is 13.249999999999998, dimensions outer_radius value 132.5. The note says cm_to_mm (x10). So the profile radius is in cm? Actually 13.25 cm = 132.5 mm. So the profile radius is 13.25 cm, which is 132.5 mm. The inner radius 7.5 cm = 75 mm. So we use the dimensions values: outer_radius=132.5, inner_radius=75.0, extrude_distance=100.0.

# Build the annulus: outer circle radius 132.5, inner circle radius 75.0, extrude 100.0 mm in +w direction.
# The frame has u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0). So w is along x-axis.
# We'll create the sketch on the YZ plane (normal to x), then extrude along x.

result = (
    cq.Workplane("YZ")
    .circle(132.5)
    .circle(75.0)  # inner hole
    .extrude(100.0)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\107668_cf76b132_0001\neg_01/generated.step")
