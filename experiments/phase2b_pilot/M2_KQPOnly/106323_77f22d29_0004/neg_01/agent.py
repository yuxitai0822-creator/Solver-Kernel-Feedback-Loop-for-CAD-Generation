import cadquery as cq

# Parameters from design plan (dimensions section, in mm)
outer_radius = 17.5
inner_radius = 12.5
extrude_distance = 10.0

# Build the bearing as an extruded annulus
# The extrude extent is symmetric, so we extrude half the total distance in both directions
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance / 2.0, both=True)
)

# Export to STEP file
cq.exporters.export(result, OUT_STEP_PATH)