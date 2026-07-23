import cadquery as cq

# Washer parameters (converted from cm to mm as noted in compiler_notes)
outer_radius = 5.5372
inner_radius = 1.9812
thickness = 1.3208

# Create the washer as an extruded annulus
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(thickness)
)

# Export to STEP file
cq.exporters.export(result, OUT_STEP_PATH)