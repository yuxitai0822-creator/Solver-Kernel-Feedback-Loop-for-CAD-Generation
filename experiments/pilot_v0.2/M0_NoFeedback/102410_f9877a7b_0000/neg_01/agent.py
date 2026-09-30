import cadquery as cq

# Build an extruded annulus (bearing-like part)
# Outer radius: 6.0 mm, Inner radius: 4.25 mm, Extrude distance: 11.5 mm
result = (
    cq.Workplane("XY")
    .circle(6.0)
    .circle(4.25)
    .extrude(11.5)
)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)