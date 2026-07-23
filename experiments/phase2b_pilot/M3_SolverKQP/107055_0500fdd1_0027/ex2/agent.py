import cadquery as cq

# Washer dimensions (converted from cm to mm as noted in compiler_notes)
outer_radius = 3.49
inner_radius = 2.0
thickness = 0.36

# Build the washer as an extruded annulus
result = (cq.Workplane("XY")
           .circle(outer_radius)
           .circle(inner_radius)
           .extrude(thickness))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)