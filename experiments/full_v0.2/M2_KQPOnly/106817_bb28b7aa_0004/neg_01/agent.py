import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions (in mm):
#   Outer radius = 5.5372 mm
#   Inner radius = 1.9812 mm
#   Thickness (extrude distance) = 1.3208 mm
# The profile center in UV is at (-25.400001, 12.7) but we place the sketch at origin for simplicity.
# The frame orientation: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0).
# We'll create the annulus on the XY plane (normal = (0,0,1)) and then rotate to match frame.

# Step 1: Create the outer circle (wire) and inner circle (wire) on the XY plane.
outer_radius = 5.5372
inner_radius = 1.9812
thickness = 1.3208

# Build the washer by extruding a circle and then cutting a concentric circle.
# Using CadQuery's workplane approach:
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)  # creates a second circle inside; when extruded, it becomes a hole
    .extrude(thickness)
)

# The resulting solid is a flat washer centered at origin, with normal along Z.
# The design plan frame has w_dir = (0,1,0) meaning the extrusion direction is Y.
# So we need to rotate the part: align Z axis to Y axis.
# Rotation: rotate 90 degrees around X axis (so Z->Y).
result = result.rotate((0,0,0), (1,0,0), -90)

# Now the washer lies in the XZ plane, extruded along Y.
# The design plan also has v_dir = (0,0,-1) which is the secondary axis.
# Our current orientation: after rotation, the original XY plane becomes XZ? Let's check:
#   Original: XY plane normal = Z. After -90 deg around X: Z->Y, Y->-Z, X->X.
#   So the face normal becomes Y, extrusion along Y. That matches w_dir = (0,1,0).
#   The v_dir in plan is (0,0,-1). In our result, the original Y axis (now -Z) is the secondary axis.
#   That is fine; the exact orientation of the profile within the plane is not critical for a washer.

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106817_bb28b7aa_0004\\neg_01/generated.step")
