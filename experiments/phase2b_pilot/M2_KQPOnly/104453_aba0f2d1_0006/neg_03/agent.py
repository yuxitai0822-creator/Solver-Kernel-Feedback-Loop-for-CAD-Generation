import cadquery as cq

# Outer rectangle: 50 x 30 (in mm)
outer_rect = cq.Workplane("XY").rect(50, 30)

# Inner rectangle: 40 x 20 (in mm)
inner_rect = cq.Workplane("XY").rect(40, 20)

# Create the rectangular frame profile by subtracting inner from outer
frame_profile = outer_rect.cut(inner_rect)

# Extrude the frame profile by 500 mm in the +Z direction
result = frame_profile.extrude(500)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)